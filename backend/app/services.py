import os
import re
from sqlalchemy import func
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from .models import Transaction, User, RecurringBill
from . import db

def scrub_pii(text):
    """
    Redacts phone numbers (XXX-XXXX) and email addresses.
    """
    # Redact phone numbers (simple regex for 555-0199 style)
    text = re.sub(r'\b\d{3}-\d{4}\b', '[REDACTED]', text)
    # Redact emails
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED]', text)
    return text

def analyze_spending(user_id, days=None):
    """
    Groups transactions by category and sums the amounts.
    Returns a dictionary to support the API/Frontend.
    """
    from datetime import datetime, timedelta
    
    query = db.session.query(Transaction.category, func.sum(Transaction.amount)).filter_by(user_id=user_id)
    
    if days:
        cutoff_date = datetime.utcnow() - timedelta(days=int(days))
        query = query.filter(Transaction.date >= cutoff_date)
        
    results = query.group_by(Transaction.category).all()
    
    # Return as dict (Frontend expects this structure)
    spending = {r[0]: round(abs(r[1]), 2) for r in results if r[1] is not None}
    return spending

def get_cashflow_history(user_id, months=6):
    """
    Returns monthly income vs expenses for the last N months.
    """
    from datetime import datetime, timedelta
    from sqlalchemy import extract
    
    # Calculate cutoff based on months
    days = int(months) * 30
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Group by Year-Month
    # SQLite doesn't have easy date truncation, so we'll fetch and process in python for MVP
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.date >= cutoff_date
    ).order_by(Transaction.date).all()
    
    history = {}
    
    for t in transactions:
        month_key = t.date.strftime('%Y-%m')
        if month_key not in history:
            history[month_key] = {'income': 0, 'expense': 0}
            
        if t.amount > 0:
            history[month_key]['income'] += t.amount
        else:
            history[month_key]['expense'] += abs(t.amount)
            
    # Convert to list sorted by date
    result = []
    for key in sorted(history.keys()):
        result.append({
            'month': key,
            'income': round(history[key]['income'], 2),
            'expense': round(history[key]['expense'], 2)
        })
        
    return result

def generate_chat_response(user_id, question):
    """
    Agentic Advisor RAG Chatbot:
    1. Context Assembly: Real calculations (90 days).
    2. Persona-Aware System Prompt.
    3. JSON Output.
    """
    from .models import MoneyScript
    from sqlalchemy import desc
    from datetime import datetime, timedelta
    import json
    import time

    t_start = time.time()

    # 1. Scrub PII
    t_scrub_start = time.time()
    clean_question = scrub_pii(question)
    t_scrub_end = time.time()
    pii_ms = (t_scrub_end - t_scrub_start) * 1000
    
    # 2. Context Assembly
    t_sql_start = time.time()
    user = User.query.get(user_id)
    ms_profile = MoneyScript.query.filter_by(user_id=user_id).first()
    
    risk_score = ms_profile.risk_score if ms_profile else 50
    persona = ms_profile.primary_persona if ms_profile else "Unknown"
    
    # --- Real Financial Calculations (Last 90 Days) ---
    ninety_days_ago = datetime.utcnow() - timedelta(days=90)
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.date >= ninety_days_ago
    ).all()
    
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    surplus = total_income - total_expenses
    
    # Find Top Category
    category_totals = {}
    for t in transactions:
        if t.amount < 0:
            cat = t.category
            category_totals[cat] = category_totals.get(cat, 0) + abs(t.amount)
            
    if category_totals:
        top_category = max(category_totals, key=category_totals.get)
        top_category_amount = category_totals[top_category]
    else:
        top_category = "None"
        top_category_amount = 0.0

    # Fetch Recommendations (Top 3) for context
    recs = get_hybrid_recommendations(user_id)[:3]
    reco_list = ", ".join([f"{r['product']} ({r['reason']})" for r in recs])

    # Detect Upcoming Bills
    bill_summary = detect_upcoming_bills(user_id)
    
    t_sql_end = time.time()
    sql_ms = (t_sql_end - t_sql_start) * 1000
    
    # 3. Setup LLM
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"answer": "Error: GEMINI_API_KEY not found.", "sources": []}
        
    llm = ChatGoogleGenerativeAI(model="models/gemini-flash-lite-latest", google_api_key=api_key)
    
    # 4. Persona-Specific Instructions
    behavioral_instruction = ""
    if persona == 'Conservative Protector' or risk_score < 40:
        behavioral_instruction = "Your client is Conservative. Prioritize safety, emergency funds, and debt reduction."
    elif persona == 'Growth Seeker' or risk_score > 70:
        behavioral_instruction = "Your client is a Growth Seeker. Focus on ROI and wealth building."
    else:
        behavioral_instruction = "Your client is Balanced. Provide a mix of stability and growth."

    # 5. Enhanced System Prompt
    system_message = SystemMessage(content=f"""
    You are a professional Financial Advisor AI dedicated to a {persona} client (Risk Score: {risk_score}/100).
    
    Financial Context (Last 90 Days):
    - Total Income: ${total_income:.2f}
    - Total Expenses: ${total_expenses:.2f}
    - Net Surplus: ${surplus:.2f}
    - Top Spending Category: {top_category} (${top_category_amount:.2f})
    - Top Recommendations: {reco_list}
    - Recurring Bills Awareness: {bill_summary}
    
    Behavioral Rules:
    {behavioral_instruction}
    
    Guidelines:
    1. Be concise, empathetic, and actionable.
    2. ALWAYS reference their specific data (e.g., "Your top spending is {top_category}...").
    3. If the user asks "what do I spend most on?", answer clearly: "Your top spending category is {top_category} at ${top_category_amount:.2f}." Use bullet points for lists.
    4. PRIVACY ALERT: Do not store or repeat PII.
    5. DISCLAIMER: Do not predict specific stock prices.
    6. You have access to the user's Spending History, Active Goals, and estimated Upcoming Recurring Bills.
    7. If the user asks "Can I afford X?", you MUST check if they have enough surplus after accounting for their upcoming bills and goal contributions.
    8. Always advise prioritizing bill payments before discretionary spending.
    
    Current User Question: {clean_question}
    """)
    
    human_message = HumanMessage(content=clean_question)
    
    t_llm_start = time.time()
    try:
        response = llm.invoke([system_message, human_message])
        ai_response = response.content
        t_llm_end = time.time()
        llm_ms = (t_llm_end - t_llm_start) * 1000
        
        total_ms = (t_llm_end - t_start) * 1000
        
        # Construct JSON response
        # In a real RAG, sources would be specific chunks. Here we cite the analysis.
        result = {
            "answer": ai_response,
            "sources": ["Financial Analysis (90 Days)", f"Top Category: {top_category}"],
            "timing_breakdown": {
                "sql_ms": round(sql_ms, 2),
                "pii_ms": round(pii_ms, 2),
                "llm_ms": round(llm_ms, 2),
                "total_ms": round(total_ms, 2)
            }
        }
        return result
        
    except Exception as e:
        return {"answer": f"Error generating response: {str(e)}", "sources": []}

def get_hybrid_recommendations(user_id):
    """
    Hybrid Recommendation Engine (Rules + SVD + Risk Filter).
    """
    import pickle
    import pandas as pd
    import numpy as np
    from .models import MoneyScript, Product
    from datetime import datetime, timedelta
    
    recommendations = []
    user = User.query.get(user_id)
    if not user:
        return []

    # --- Layer 1: Rule-Based (Financial Health Check) ---
    
    # Fetch transactions from last 90 days
    ninety_days_ago = datetime.utcnow() - timedelta(days=90)
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.date >= ninety_days_ago
    ).all()
    
    # Calculate Monthly Expenses (Avg of negative txs over 3 months)
    total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    monthly_expenses = total_expenses / 3 if total_expenses > 0 else 0

    # Calculate Total Savings (Sum of 'Savings' category or positive transfers)
    # For MVP, we'll sum positive transactions in 'Savings' category from the fetched batch
    # In a real app, this would be a balance check.
    total_savings = sum(t.amount for t in transactions if t.category == 'Savings' and t.amount > 0)
    
    # Rule A: Emergency Fund Builder
    if total_savings < (3 * monthly_expenses):
        savings_products = Product.query.filter_by(category='Savings').all()
        for p in savings_products:
            recommendations.append({
                'product': p.name,
                'reason': 'Emergency Fund Builder: You should aim for 3-6 months of expenses.',
                'score': 0.95,
                'source': 'Rule: Financial Health'
            })

    # Rule B: Debt Optimization
    # Count 'Credit Card Payment' transactions
    cc_payments = sum(1 for t in transactions if 'Credit Card Payment' in t.description or t.category == 'Debt')
    
    if cc_payments > 5:
        debt_products = Product.query.filter(Product.name.like('%Debt%')).all()
        for p in debt_products:
            recommendations.append({
                'product': p.name,
                'reason': 'Debt Optimization: We noticed frequent credit card payments.',
                'score': 0.90,
                'source': 'Rule: Financial Health'
            })

    # --- Layer 2: Collaborative Filtering (SVD) ---
    try:
        model_path = os.path.join(os.path.dirname(__file__), '../svd_model.pkl')
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
            
        svd = model_data['svd_model']
        product_ids = model_data['product_columns']
        user_factors = model_data['user_factors']
        
        # Get User's Risk Score to map to synthetic profile
        ms_profile = MoneyScript.query.filter_by(user_id=user_id).first()
        risk_score = ms_profile.risk_score if ms_profile else 50
        
        # Find closest synthetic user profile (0-99)
        # Our synthetic data generation mapped 0-30 to Safe (Low Risk) and 70-100 to Risky.
        # So mapping risk_score directly to index is a good approximation.
        synthetic_idx = min(99, int(risk_score))
        
        # Get the latent factors for this profile
        user_vector = user_factors[synthetic_idx]
        
        # Predict scores: dot product of user vector and item vectors
        scores = np.dot(user_vector, svd.components_)
        
        # Get top 3 indices
        top_indices = scores.argsort()[::-1][:3]
        
        for idx in top_indices:
            p_id = product_ids[idx]
            product = Product.query.get(p_id)
            
            if product:
                # Avoid duplicates
                if not any(r['product'] == product.name for r in recommendations):
                    recommendations.append({
                        'product': product.name,
                        'reason': 'People like you use this.',
                        'score': 0.85, 
                        'source': 'AI Recommendation (SVD)'
                    })
                
    except Exception as e:
        print(f"SVD Model Error: {e}")

    # --- Layer 3: Risk Filter (Safety Layer) ---
    ms_profile = MoneyScript.query.filter_by(user_id=user_id).first()
    risk_score = ms_profile.risk_score if ms_profile else 50
    primary_persona = ms_profile.primary_persona if ms_profile else 'Unknown'
    
    final_recs = []
    for rec in recommendations:
        # Fetch product details
        p_obj = Product.query.filter_by(name=rec['product']).first()
        if not p_obj:
            continue
            
        # Filter Logic
        # If Conservative Protector OR Risk Score < 40, filter out High Risk
        if (primary_persona == 'Conservative Protector' or risk_score < 40) and p_obj.risk_level == 'High':
            continue # REMOVE High Risk for Conservative users
            
        final_recs.append(rec)
        
    # Sort by score
    final_recs.sort(key=lambda x: x['score'], reverse=True)
    
    return final_recs[:5]

def analyze_savings_plan(user_id, goal_amount, target_date=None):
    """
    Analyzes cashflow and generates a savings plan with scenarios.
    """
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta
    import math

    # 1. Analyze Cashflow (Last 90 Days)
    cutoff_date = datetime.now() - timedelta(days=90)
    
    # Fetch all transactions for last 90 days
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.date >= cutoff_date
    ).all()

    income_total = 0
    fixed_expenses = 0
    
    # Specific Summation for Discretionary (Food + Shopping)
    food_sum = 0
    shopping_sum = 0
    
    # Keywords/Categories mapping
    fixed_categories = ['Bills', 'Subscription', 'Utilities', 'Rent', 'Mortgage']
    food_cats = ['Food', 'Groceries', 'Dining', 'Restaurants', 'Bars']
    shopping_cats = ['Shopping', 'Clothing', 'Electronics']

    for t in transactions:
        if t.amount > 0:
            income_total += t.amount
        else:
            amount = abs(t.amount)
            # Fixed Expenses
            if t.category in fixed_categories:
                fixed_expenses += amount
            
            # Discretionary Summation
            if t.category in food_cats:
                food_sum += amount
            elif t.category in shopping_cats:
                shopping_sum += amount

    # Calculate Monthly Averages (Divide by 3)
    avg_income = income_total / 3
    avg_fixed = fixed_expenses / 3
    avg_food = food_sum / 3
    avg_shopping = shopping_sum / 3
    
    # Total Discretionary for Surplus Calc
    total_avg_discretionary = avg_food + avg_shopping

    # 2. Scenario A: Current Pace
    current_surplus = avg_income - (avg_fixed + total_avg_discretionary)
    current_surplus = max(0, current_surplus) # Avoid negative surplus for calculation

    months_to_goal_a = math.ceil(goal_amount / current_surplus) if current_surplus > 0 else 999
    date_a = datetime.now() + relativedelta(months=months_to_goal_a)

    # 3. Scenario B: Smart Squeeze (Cut Food by 20%)
    # We focus on Food as the primary discretionary lever for this feature
    savings_potential = avg_food * 0.20
    optimized_surplus = current_surplus + savings_potential
    
    months_to_goal_b = math.ceil(goal_amount / optimized_surplus) if optimized_surplus > 0 else 999
    date_b = datetime.now() + relativedelta(months=months_to_goal_b)

    # 4. Feasibility Check (if target_date provided)
    feasibility_status = "N/A"
    required_contribution = 0
    insight_text = ""

    if target_date:
        try:
            # Handle YYYY-MM-DD format
            target_dt = datetime.strptime(target_date, '%Y-%m-%d')
            today = datetime.now()
            
            # Calculate months remaining
            diff = relativedelta(target_dt, today)
            months_remaining = diff.years * 12 + diff.months + (diff.days / 30.0)
            months_remaining = max(1, round(months_remaining)) # Minimum 1 month
            
            required_contribution = goal_amount / months_remaining
            
            if current_surplus >= required_contribution:
                feasibility_status = "Achievable"
                insight_text = f"You're on track! Your surplus of ${current_surplus:.0f}/mo covers the ${required_contribution:.0f}/mo needed."
            elif optimized_surplus >= required_contribution:
                feasibility_status = "Stretch"
                insight_text = f"To hit your date, you need ${required_contribution:.0f}/mo. Cutting food spend by 20% gets you to ${optimized_surplus:.0f}/mo."
            else:
                feasibility_status = "Unrealistic"
                insight_text = f"You need ${required_contribution:.0f}/mo, but even with cuts you only have ${optimized_surplus:.0f}. Consider extending the date."
                
        except Exception as e:
            print(f"Date parsing error: {e}")
            # Fallback to default insight
            insight_text = (
                f"You spend ~${avg_food:.0f} on Food. "
                f"Cutting this by 20% saves ${savings_potential:.0f}/mo "
                f"and helps you reach your goal by {date_b.strftime('%B %Y')}."
            )
    else:
        # Default Insight if no date
        insight_text = (
            f"You spend ~${avg_food:.0f} on Food. "
            f"Cutting this by 20% saves ${savings_potential:.0f}/mo "
            f"and helps you reach your goal by {date_b.strftime('%B %Y')}."
        )

    return {
        "current_monthly_save": round(current_surplus, 2),
        "optimized_monthly_save": round(optimized_surplus, 2),
        "required_monthly_contribution": round(required_contribution, 2),
        "feasibility_status": feasibility_status,
        "insight_text": insight_text,
        "scenarios": {
            "current": {
                "months": months_to_goal_a,
                "completion_date": date_a.strftime('%Y-%m-%d')
            },
            "optimized": {
                "months": months_to_goal_b,
                "completion_date": date_b.strftime('%Y-%m-%d'),
                "strategy": "Cut Food by 20%"
            }
        }
    }

def calculate_persona(quiz_answers):
    """
    Calculates risk score and determines financial persona based on quiz answers.
    
    Args:
        quiz_answers (dict): Dictionary of question IDs and answer values (e.g., {'q1': 10, 'q2': 20})
        
    Returns:
        tuple: (risk_score, primary_persona)
    """
    # Calculate Risk Score
    # Sum the values of the answers. 
    # Assuming answers are integers representing points.
    risk_score = sum(int(val) for val in quiz_answers.values() if str(val).isdigit())
    
    # Ensure score is within 0-100 bounds (optional safety)
    risk_score = max(0, min(100, risk_score))

    # Determine Persona
    if risk_score < 40:
        primary_persona = 'Conservative Protector'
    elif risk_score <= 70:
        primary_persona = 'Balanced Strategist'
    else:
        primary_persona = 'Growth Seeker'
        
    return risk_score, primary_persona

def detect_recurring_bills(user_id):
    """
    Scans recent transactions to identify recurring bills.
    Updates the RecurringBill table.
    """
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    # Get transactions from last 90 days
    cutoff = datetime.utcnow() - timedelta(days=90)
    txs = Transaction.query.filter(Transaction.user_id == user_id, Transaction.date >= cutoff).all()
    
    # Group by vendor/merchant
    groups = defaultdict(list)
    for t in txs:
        # Use merchant_clean if available, else vendor, else description
        name = t.merchant_clean or t.vendor or t.description
        if name:
            groups[name].append(t)
            
    detected = []
    for name, transactions in groups.items():
        # Need at least 2 transactions to establish a pattern
        if len(transactions) >= 2:
            # Check if dates are roughly monthly (25-35 days apart)
            transactions.sort(key=lambda x: x.date)
            intervals = []
            for i in range(1, len(transactions)):
                delta = (transactions[i].date - transactions[i-1].date).days
                intervals.append(delta)
            
            if not intervals:
                continue
                
            avg_interval = sum(intervals) / len(intervals)
            
            # Allow for some variance (e.g. 20-40 days for monthly)
            if 20 <= avg_interval <= 40:
                # It's likely monthly
                avg_amount = sum(t.amount for t in transactions) / len(transactions)
                # Use the day of the most recent transaction as the due day
                day_of_month = transactions[-1].date.day
                
                # Check if already exists
                existing = RecurringBill.query.filter_by(user_id=user_id, vendor_name=name).first()
                if not existing:
                    bill = RecurringBill(
                        user_id=user_id,
                        vendor_name=name,
                        average_amount=abs(avg_amount),
                        day_of_month=day_of_month,
                        frequency='Monthly'
                    )
                    db.session.add(bill)
                    detected.append(name)
                else:
                    # Update average amount and day to keep it fresh
                    existing.average_amount = abs(avg_amount)
                    existing.day_of_month = day_of_month
                    existing.is_active = True
                    
    if detected:
        db.session.commit()
        print(f"Detected new bills: {detected}")
    
    return detected

def detect_upcoming_bills(user_id):
    """
    Analyzes recent transactions to find known billers and estimate next due dates.
    Returns a summary string for the chatbot context.
    """
    from datetime import datetime, timedelta
    
    # 1. Refresh Recurring Bills from recent transactions
    # This ensures our DB is up-to-date with the latest transaction patterns
    detect_recurring_bills(user_id)
    
    # 2. Fetch Active Recurring Bills from DB
    bills = RecurringBill.query.filter_by(user_id=user_id, is_active=True).all()
    
    if not bills:
        return "No upcoming recurring bills detected."
        
    found_bills = []
    total_estimated = 0
    today = datetime.utcnow()
    
    for bill in bills:
        # Calculate next due date
        try:
            # Create a date object for this month with the bill's due day
            # Handle months with fewer days (e.g. Feb) by wrapping in try/except or logic
            # For simplicity, we'll try to set the day. If it fails (e.g. Feb 30), we skip/adjust.
            
            # Determine if the due date for this month has passed
            if today.day <= bill.day_of_month:
                # Due later this month
                target_month = today.month
                target_year = today.year
            else:
                # Due next month
                if today.month == 12:
                    target_month = 1
                    target_year = today.year + 1
                else:
                    target_month = today.month + 1
                    target_year = today.year
            
            # Handle end of month days (e.g. 31st)
            # If the target month doesn't have that day, pick the last day of that month
            import calendar
            _, last_day = calendar.monthrange(target_year, target_month)
            due_day = min(bill.day_of_month, last_day)
            
            next_due = today.replace(year=target_year, month=target_month, day=due_day)
            
        except Exception as e:
            # Fallback: just add 30 days to today if calculation fails
            next_due = today + timedelta(days=30)

        found_bills.append({
            'name': bill.vendor_name,
            'amount': bill.average_amount,
            'due_date': next_due.strftime('%Y-%m-%d')
        })
        total_estimated += bill.average_amount

    # Sort by due date
    found_bills.sort(key=lambda x: x['due_date'])

    # 4. Generate Summary String
    bill_details = ", ".join([f"{b['name']} (~${b['amount']:.0f} due {b['due_date']})" for b in found_bills])
    summary = f"Upcoming Bills: {bill_details}. Total estimated monthly fixed costs: ~${total_estimated:.0f}."
    
    return summary

def generate_financial_insights(user_id):
    """
    Analyzes user data to return a list of actionable insight objects.
    Rules-Based Engine: Spending Leaks, Goal Acceleration, Safety Net.
    """
    from datetime import datetime, timedelta
    from .models import Goal
    
    insights = []
    
    # 1. Data Gathering
    # Fetch active goals
    active_goals = Goal.query.filter_by(user_id=user_id).all()
    
    # Fetch transactions for last 30 days
    cutoff = datetime.utcnow() - timedelta(days=30)
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id, 
        Transaction.date >= cutoff
    ).all()
    
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    monthly_surplus = total_income - total_expenses
    
    # Group expenses by category
    category_expenses = {}
    for t in transactions:
        if t.amount < 0:
            cat = t.category
            category_expenses[cat] = category_expenses.get(cat, 0) + abs(t.amount)
            
    # 2. Rule 1: The "Spending Leak" Insight
    # Find highest discretionary spending category
    # We'll consider everything except 'Bills', 'Rent', 'Mortgage', 'Utilities' as potentially discretionary for this rule
    # Or just pick the absolute highest category and check if it's > 20% of total expenses
    
    if total_expenses > 0:
        sorted_cats = sorted(category_expenses.items(), key=lambda x: x[1], reverse=True)
        
        # Filter out obvious fixed costs if possible, or just warn about the highest one
        # Let's try to filter out 'Rent', 'Mortgage', 'Bills' to focus on "Leaks"
        fixed_keywords = ['Rent', 'Mortgage', 'Bills', 'Utilities', 'Transfer']
        
        leak_candidate = None
        for cat, amount in sorted_cats:
            if cat not in fixed_keywords:
                leak_candidate = (cat, amount)
                break
                
        if leak_candidate:
            cat, amount = leak_candidate
            if amount > (total_expenses * 0.20):
                insights.append({
                    'type': 'warning',
                    'title': f'High {cat} Spend',
                    'message': f'You spent ${amount:.0f} on {cat} this month. Cutting this by 25% could save you ${(amount * 0.25):.0f} towards your goals.',
                    'action': f'Set {cat} Budget'
                })

    # 3. Rule 2: The "Goal Acceleration" Insight
    if active_goals and monthly_surplus > 100:
        top_goal = active_goals[0] # Pick first one
        insights.append({
            'type': 'opportunity',
            'title': 'Accelerate Your Goal',
            'message': f'You have a healthy surplus of ${monthly_surplus:.0f} this month. Consider adding an extra $100 to your {top_goal.name} goal to finish it faster.',
            'action': 'Boost Goal'
        })

    # 4. Rule 3: The "Safety Net" Insight (Fallback)
    if monthly_surplus < 0:
        insights.append({
            'type': 'critical',
            'title': 'Spending Alert',
            'message': 'You are currently spending more than you earn this month. Review your recent transactions to find cutbacks.',
            'action': 'Review Transactions'
        })
        
    # Limit to top 3
    return insights[:3]

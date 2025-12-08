from flask import Blueprint, request, jsonify
from . import db, limiter
from .models import User, Transaction, Goal, SystemLog
from .services import analyze_spending, generate_chat_response, get_cashflow_history, get_hybrid_recommendations
from .auth_middleware import verify_token
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from .import_utils import parse_pdf

main = Blueprint('main', __name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'statements')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@main.route('/api/upload-statements', methods=['POST'])
@verify_token
def upload_statements():
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    if 'files' not in request.files:
        return jsonify({'error': 'No files part'}), 400
        
    files = request.files.getlist('files')
    total_tx = 0
    
    for file in files:
        if file.filename == '':
            continue
            
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            try:
                transactions = parse_pdf(file_path)
                for tx_data in transactions:
                    tx = Transaction(
                        user_id=user.id,
                        date=tx_data['date'],
                        description=tx_data['description'],
                        amount=tx_data['amount'],
                        category=tx_data['category'],
                        vendor=tx_data['vendor'],
                        merchant_clean=tx_data['merchant_clean'],
                        type=tx_data['type'],
                        balance_after=tx_data['balance_after']
                    )
                    db.session.add(tx)
                total_tx += len(transactions)
            except Exception as e:
                print(f"Error parsing {filename}: {str(e)}")
                continue
                
    db.session.commit()
    return jsonify({'message': f'Successfully uploaded and parsed {total_tx} transactions.'}), 200

@main.route('/api/log-click', methods=['POST'])
@verify_token
def log_click():
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    data = request.json
    product_id = data.get('product_id')
    reason = data.get('recommendation_reason')
    
    log_entry = SystemLog(
        user_id=user.id,
        event_type='reco_click',
        details=f"Product ID: {product_id}, Reason: {reason}"
    )
    db.session.add(log_entry)
    db.session.commit()
    
    return jsonify({"status": "logged"}), 200

@main.route('/api/sync-user', methods=['POST'])
@verify_token
def sync_user():
    """
    Syncs the user from Firebase to the local DB.
    If the user is new, clone transactions from the Seed User (test_user_123).
    """
    uid = request.user['uid']
    email = request.user.get('email')
    
    user = User.query.filter_by(firebase_uid=uid).first()
    
    if not user:
        # Create new user
        user = User(firebase_uid=uid, email=email)
        db.session.add(user)
        db.session.commit()
    
    # Check if user has transactions, if not, clone from Seed User
    # tx_count = Transaction.query.filter_by(user_id=user.id).count()
    # if tx_count == 0:
    #     seed_user = User.query.filter_by(firebase_uid='test_user_123').first()
    #     if seed_user:
    #         seed_transactions = Transaction.query.filter_by(user_id=seed_user.id).all()
    #         for st in seed_transactions:
    #             new_tx = Transaction(
    #                 user_id=user.id,
    #                 date=st.date,
    #                 description=st.description,
    #                 amount=st.amount,
    #                 category=st.category,
    #                 vendor=st.vendor
    #             )
    #             db.session.add(new_tx)
    #         db.session.commit()
    #         print(f"Cloned {len(seed_transactions)} transactions for user {uid}")
            
    # Check Onboarding Status
    from .models import MoneyScript
    ms = MoneyScript.query.filter_by(user_id=user.id).first()
    onboarding_completed = True if ms else False

    return jsonify({
        'message': 'User synced', 
        'user_id': user.id,
        'onboarding_completed': onboarding_completed
    }), 200

@main.route('/api/profile', methods=['PUT'])
@verify_token
def update_profile():
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    data = request.get_json()
    
    if 'age' in data:
        user.age = data['age']
    if 'income' in data:
        user.annual_income = data['income']
        
    # Recalculate income level
    if user.annual_income:
        try:
            income_val = float(user.annual_income)
            if income_val < 50000:
                user.income_level = 'Low'
            elif income_val < 150000:
                user.income_level = 'Medium'
            else:
                user.income_level = 'High'
        except ValueError:
            pass
            
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200

@main.route('/api/transactions', methods=['GET'])
@verify_token
def get_transactions():
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # Filtering
    query = Transaction.query.filter_by(user_id=user.id)
    
    category = request.args.get('category')
    if category and category != 'All':
        query = query.filter(Transaction.category == category)
        
    # Duration Filter (New)
    duration = request.args.get('duration')
    if duration and duration != 'ALL':
        try:
            days = int(duration)
            start_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Transaction.date >= start_date)
        except ValueError:
            pass
        
    start_date_param = request.args.get('start_date')
    if start_date_param:
        query = query.filter(Transaction.date >= datetime.strptime(start_date_param, '%Y-%m-%d'))
        
    end_date_param = request.args.get('end_date')
    if end_date_param:
        query = query.filter(Transaction.date <= datetime.strptime(end_date_param, '%Y-%m-%d'))
        
    transactions = query.order_by(Transaction.date.desc()).all()
    
    data = [{
        'id': t.id,
        'date': t.date.strftime('%Y-%m-%d'),
        'description': t.description,
        'amount': t.amount,
        'category': t.category,
        'vendor': t.vendor,
        'merchant_clean': t.merchant_clean,
        'type': t.type
    } for t in transactions]
    
    return jsonify(data), 200

@main.route('/api/analysis', methods=['GET'])
@verify_token
def get_analysis():
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # Duration Filter
    duration = request.args.get('duration', '30') # Default 30 days
    print(f"DEBUG: get_analysis called with duration={duration} for user {user.id}")
    
    days = None
    months = 6
    
    if duration == 'ALL':
        days = None
        months = 24 # Cap at 2 years for history
    else:
        try:
            days = int(duration)
            months = max(6, int(days / 30)) # At least 6 months history
        except ValueError:
            days = 30
            
    # 1. Spending by Category
    spending = analyze_spending(user.id, days=days)
    
    # 2. Cashflow History
    from .services import get_cashflow_history
    cashflow = get_cashflow_history(user.id, months=months)
    
    # 3. Risk Score
    from .models import MoneyScript
    ms = MoneyScript.query.filter_by(user_id=user.id).first()
    risk_score = ms.risk_score if ms else 50
    
    return jsonify({
        'spending': spending,
        'cashflow': cashflow,
        'risk_score': risk_score
    }), 200

@main.route('/api/chat', methods=['POST'])
@verify_token
@limiter.limit("10 per minute")
def chat():
    """
    Chat with the AI assistant.
    """
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    data = request.get_json()
    question = data.get('message')
    
    if not question:
        return jsonify({'error': 'Message required'}), 400
        
    response = generate_chat_response(user.id, question)
    return jsonify({'response': response}), 200

@main.route('/api/audit', methods=['GET'])
def audit():
    """
    Run Red Team Audit.
    Note: In production, this should be protected by Admin auth.
    """
    from .audit_utils import run_red_team_audit
    results = run_red_team_audit()
    return jsonify(results), 200

@main.route('/api/goals', methods=['GET'])
@verify_token
def get_goals():
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    goals = Goal.query.filter_by(user_id=user.id).all()
    data = [{
        'id': g.id,
        'name': g.name,
        'target_amount': g.target_amount,
        'current_amount': g.current_amount,
        'target_date': g.target_date.strftime('%Y-%m-%d') if g.target_date else None
    } for g in goals]
    
    return jsonify(data), 200

@main.route('/api/goals', methods=['POST'])
@verify_token
def add_goal():
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    data = request.get_json()
    
    # Basic validation
    if not data.get('name') or not data.get('target_amount'):
        return jsonify({'error': 'Name and Target Amount are required'}), 400
        
    try:
        target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date() if data.get('target_date') else None
    except ValueError:
        return jsonify({'error': 'Invalid date format (YYYY-MM-DD)'}), 400

    new_goal = Goal(
        user_id=user.id,
        name=data['name'],
        target_amount=float(data['target_amount']),
        current_amount=float(data.get('current_amount', 0)),
        target_date=target_date
    )
    
    db.session.add(new_goal)
    db.session.commit()
    
    return jsonify({'message': 'Goal created', 'id': new_goal.id}), 201

@main.route('/api/onboarding', methods=['POST'])
@verify_token
def onboarding():
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    data = request.get_json()
    
    # 1. Update Demographics
    user.age = data.get('age')
    user.annual_income = data.get('income')
    
    # Derive income_level
    if user.annual_income:
        try:
            income_val = float(user.annual_income)
            if income_val < 50000:
                user.income_level = 'Low'
            elif income_val < 150000:
                user.income_level = 'Medium'
            else:
                user.income_level = 'High'
        except ValueError:
            pass # Keep default if invalid
            
    # 2. Calculate Persona
    quiz_answers = data.get('quiz_answers', {})
    from .services import calculate_persona
    risk_score, primary_persona = calculate_persona(quiz_answers)
    
    # 3. Save/Update MoneyScript Profile
    from .models import MoneyScript
    profile = MoneyScript.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = MoneyScript(user_id=user.id)
        db.session.add(profile)
    
    profile.risk_score = risk_score
    profile.primary_persona = primary_persona
    profile.quiz_data = quiz_answers
    # Infer time horizon from risk score for now
    profile.time_horizon = 'Long' if risk_score > 60 else 'Short'
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'persona': primary_persona,
        'risk_score': risk_score
    }), 200

@main.route('/api/profile', methods=['GET'])
@verify_token
def get_profile():
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    from .models import MoneyScript
    ms = MoneyScript.query.filter_by(user_id=user.id).first()
    
    return jsonify({
        'email': user.email,
        'age': user.age,
        'income': user.annual_income,
        'income_level': user.income_level,
        'risk_score': ms.risk_score if ms else 50,
        'persona': ms.primary_persona if ms else 'Unknown',
        'quiz_data': ms.quiz_data if ms else {}
    }), 200

@main.route('/api/recommend', methods=['GET'])
@verify_token
@limiter.limit("50 per minute")
def recommend():
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    from .services import generate_financial_insights
    recs = generate_financial_insights(user.id)
    
    return jsonify(recs), 200

@main.route('/api/insights', methods=['GET'])
@verify_token
def get_insights():
    """
    Get AI-generated financial insights.
    """
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    from .services import generate_financial_insights
    insights = generate_financial_insights(user.id)
    return jsonify(insights), 200

@main.route('/api/savings-plan', methods=['POST'])
@verify_token
def savings_plan():
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    data = request.get_json()
    goal_amount = data.get('goal_amount')
    target_date = data.get('target_date') # Optional
    
    if not goal_amount:
        return jsonify({'error': 'Goal amount is required'}), 400
        
    try:
        goal_amount = float(goal_amount)
    except ValueError:
        return jsonify({'error': 'Invalid goal amount'}), 400

    from .services import analyze_savings_plan
    result = analyze_savings_plan(user.id, goal_amount, target_date)
    
    return jsonify(result), 200

@main.route('/api/bills', methods=['GET'])
@verify_token
def get_bills():
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # Run detection
    from .services import detect_recurring_bills
    detect_recurring_bills(user.id)
    
    # Fetch bills
    from .models import RecurringBill
    bills = RecurringBill.query.filter_by(user_id=user.id, is_active=True).all()
    
    data = []
    today = datetime.utcnow().date()
    
    for b in bills:
        # Calculate next due date
        try:
            if today.day > b.day_of_month:
                # Next month
                if today.month == 12:
                    next_due = datetime(today.year + 1, 1, b.day_of_month).date()
                else:
                    next_due = datetime(today.year, today.month + 1, b.day_of_month).date()
            else:
                # This month
                next_due = datetime(today.year, today.month, b.day_of_month).date()
        except ValueError:
            # Handle short months (e.g. 31st in Feb)
            import calendar
            if today.day > b.day_of_month:
                month = 1 if today.month == 12 else today.month + 1
                year = today.year + 1 if today.month == 12 else today.year
            else:
                month = today.month
                year = today.year
                
            last_day = calendar.monthrange(year, month)[1]
            day = min(b.day_of_month, last_day)
            next_due = datetime(year, month, day).date()

        # Check if paid this cycle
        is_paid = False
        if b.last_paid_date:
            if b.last_paid_date.month == next_due.month and b.last_paid_date.year == next_due.year:
                is_paid = True
                
        days_remaining = (next_due - today).days
        
        status = 'Upcoming'
        if is_paid:
            status = 'Paid'
        elif days_remaining < 0:
            status = 'Overdue'
        elif days_remaining <= 10:
            status = 'Due Soon'
            
        data.append({
            'id': b.id,
            'name': b.vendor_name,
            'amount': b.average_amount,
            'dueDate': next_due.strftime('%Y-%m-%d'),
            'daysRemaining': days_remaining,
            'status': status,
            'isPaid': is_paid
        })
        
    return jsonify(data), 200

@main.route('/api/bills', methods=['POST'])
@verify_token
def add_bill():
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    data = request.get_json()
    name = data.get('name')
    amount = data.get('amount')
    day_of_month = data.get('day_of_month')
    
    if not name or not amount or not day_of_month:
        return jsonify({'error': 'Name, amount, and day of month are required'}), 400
        
    try:
        amount = float(amount)
        day_of_month = int(day_of_month)
        if not (1 <= day_of_month <= 31):
             return jsonify({'error': 'Day must be between 1 and 31'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid format'}), 400

    from .models import RecurringBill
    new_bill = RecurringBill(
        user_id=user.id,
        vendor_name=name,
        average_amount=amount,
        day_of_month=day_of_month,
        frequency='Monthly',
        is_active=True
    )
    
    db.session.add(new_bill)
    db.session.commit()
    
    return jsonify({'message': 'Bill added successfully', 'id': new_bill.id}), 201

@main.route('/api/bills/<int:bill_id>', methods=['PUT'])
@verify_token
def update_bill(bill_id):
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    from .models import RecurringBill
    bill = RecurringBill.query.filter_by(id=bill_id, user_id=user.id).first()
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
        
    data = request.get_json()
    
    if 'name' in data:
        bill.vendor_name = data['name']
    if 'amount' in data:
        try:
            bill.average_amount = float(data['amount'])
        except ValueError:
            return jsonify({'error': 'Invalid amount'}), 400
    if 'day_of_month' in data:
        try:
            day = int(data['day_of_month'])
            if 1 <= day <= 31:
                bill.day_of_month = day
            else:
                return jsonify({'error': 'Day must be between 1 and 31'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid day format'}), 400
            
    db.session.commit()
    return jsonify({'message': 'Bill updated successfully'}), 200

@main.route('/api/bills/<int:bill_id>/pay', methods=['POST'])
@verify_token
def mark_bill_paid(bill_id):
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    from .models import RecurringBill
    bill = RecurringBill.query.filter_by(id=bill_id, user_id=user.id).first()
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
        
    bill.last_paid_date = datetime.utcnow().date()
    db.session.commit()
    
    return jsonify({'message': 'Bill marked as paid'}), 200

@main.route('/api/bills/<int:bill_id>', methods=['DELETE'])
@verify_token
def delete_bill(bill_id):
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    from .models import RecurringBill
    bill = RecurringBill.query.filter_by(id=bill_id, user_id=user.id).first()
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
        
    # Soft delete (set is_active=False) or hard delete?
    # Let's do hard delete for now as requested, or soft delete if we want history.
    # User asked "can be deleted", usually implies removal.
    db.session.delete(bill)
    db.session.commit()
    
    return jsonify({'message': 'Bill deleted successfully'}), 200

@main.route('/api/goals/<int:goal_id>', methods=['PUT'])
@verify_token
def update_goal(goal_id):
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    goal = Goal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
        
    data = request.get_json()
    
    if 'name' in data:
        goal.name = data['name']
    if 'target_amount' in data:
        try:
            goal.target_amount = float(data['target_amount'])
        except ValueError:
            return jsonify({'error': 'Invalid target amount'}), 400
    if 'current_amount' in data:
        try:
            goal.current_amount = float(data['current_amount'])
        except ValueError:
            return jsonify({'error': 'Invalid current amount'}), 400
    if 'target_date' in data:
        try:
            if data['target_date']:
                goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date()
            else:
                goal.target_date = None
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
            
    db.session.commit()
    return jsonify({'message': 'Goal updated successfully'}), 200

@main.route('/api/goals/<int:goal_id>', methods=['DELETE'])
@verify_token
def delete_goal(goal_id):
    uid = request.user['uid']
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    goal = Goal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
        
    db.session.delete(goal)
    db.session.commit()
    
    return jsonify({'message': 'Goal deleted successfully'}), 200

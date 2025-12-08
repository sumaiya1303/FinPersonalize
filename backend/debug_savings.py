from app import create_app, db
from app.models import Transaction, User
from app.services import analyze_savings_plan
from datetime import datetime, timedelta
import json

app = create_app()

def debug_savings():
    with app.app_context():
        print("--- Debugging Savings Analysis ---")
        
        # 1. Total Count
        total_tx = Transaction.query.count()
        print(f"Total Transactions in DB: {total_tx}")
        
        # 2. Sum of Food (Last 90 Days)
        user = User.query.filter_by(firebase_uid='test_user_123').first()
        if not user:
            print("Test user not found.")
            return

        three_months_ago = datetime.utcnow() - timedelta(days=90)
        food_txs = Transaction.query.filter(
            Transaction.user_id == user.id,
            Transaction.date >= three_months_ago,
            Transaction.category.in_(['Food', 'Groceries'])
        ).all()
        
        food_sum = sum(abs(t.amount) for t in food_txs)
        print(f"Sum of Food/Groceries (Last 90 Days): ${food_sum:.2f}")
        
        # 3. Call Service
        print("\nCalling analyze_savings_plan...")
        result = analyze_savings_plan(user.id, 5000)
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    debug_savings()

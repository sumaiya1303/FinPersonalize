from app import create_app, db
from app.models import User, Transaction
import pandas as pd

app = create_app()

def inspect_data():
    with app.app_context():
        user = User.query.filter_by(firebase_uid='test_user_123').first()
        if not user:
            print("User not found.")
            return

        transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.date.desc()).all()
        print(f"Total Transactions Found: {len(transactions)}")
        
        if transactions:
            print("\n--- First 10 Transactions ---")
            data = []
            for t in transactions[:10]:
                data.append({
                    'Date': t.date.strftime('%Y-%m-%d'),
                    'Vendor': t.vendor,
                    'Amount': t.amount,
                    'Category': t.category,
                    'Description': t.description[:30] + '...' if len(t.description) > 30 else t.description
                })
            
            df = pd.DataFrame(data)
            print(df.to_string(index=False))
        else:
            print("No transactions found.")

if __name__ == '__main__':
    inspect_data()

from app import create_app, db
from app.models import User, Transaction

app = create_app()

def verify_data():
    with app.app_context():
        print("--- Database Verification ---")
        users = User.query.all()
        print(f"Total Users: {len(users)}")
        
        for user in users:
            tx_count = Transaction.query.filter_by(user_id=user.id).count()
            print(f"User ID: {user.id}, Email: {user.email}, UID: {user.firebase_uid}, Transactions: {tx_count}")
            
            if tx_count > 0:
                print("Sample Transactions:")
                transactions = Transaction.query.filter_by(user_id=user.id).limit(5).all()
                for t in transactions:
                    print(f"  - Date: {t.date.date()}, Desc: {t.description[:20]}..., Clean: {t.merchant_clean}, Cat: {t.category}, Type: {t.type}")

            # Check MoneyScript Profile
            from app.models import MoneyScript
            profile = MoneyScript.query.filter_by(user_id=user.id).first()
            if profile:
                print(f"MoneyScript Profile: Risk Score={profile.risk_score}, Script={profile.primary_script}, Horizon={profile.time_horizon}")
                print(f"Demographics: Age={user.age}, Income=${user.annual_income}")
            else:
                print("No MoneyScript Profile found.")

        if not users:
            print("No users found!")

if __name__ == '__main__':
    verify_data()

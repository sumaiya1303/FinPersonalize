from app import create_app, db
from app.models import User, Transaction
from datetime import datetime, timedelta
import random

app = create_app()

def generate_mock_data():
    with app.app_context():
        user = User.query.filter_by(firebase_uid='test_user_123').first()
        if not user:
            print("Creating seed user...")
            user = User(firebase_uid='test_user_123', email='test@example.com')
            db.session.add(user)
            db.session.commit()

        print(f"Generating mock transactions for user {user.id}...")
        
        vendors = {
            'Food': ['Chick-fil-A', 'Starbucks', 'McDonalds', 'Chipotle'],
            'Groceries/Shopping': ['Vons', 'Ralphs', 'Target', 'Walmart'],
            'Bills': ['Edison', 'Spectrum', 'Verizon', 'State Farm'],
            'Subscription': ['Netflix', 'Spotify', 'Hulu', 'Prime Video'],
            'General': ['Unknown Store', 'Gas Station', 'Parking']
        }

        transactions = []
        for _ in range(20): # Generate 20 transactions
            category = random.choice(list(vendors.keys()))
            vendor = random.choice(vendors[category])
            amount = round(random.uniform(10.0, 150.0), 2)
            date = datetime.now() - timedelta(days=random.randint(0, 60))
            
            tx = Transaction(
                user_id=user.id,
                date=date,
                description=f"Purchase at {vendor}",
                amount=amount,
                category=category,
                vendor=vendor
            )
            transactions.append(tx)
        
        db.session.add_all(transactions)
        db.session.commit()
        print(f"Successfully added {len(transactions)} mock transactions.")

if __name__ == '__main__':
    generate_mock_data()

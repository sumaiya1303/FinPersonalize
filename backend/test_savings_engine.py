from app import create_app, db
from app.models import User
from app.services import analyze_savings_plan
import json

app = create_app()

def test_savings():
    with app.app_context():
        # Get seed user
        user = User.query.filter_by(firebase_uid='test_user_123').first()
        if not user:
            print("Seed user not found. Please run generate_mock_data.py first.")
            return

        print(f"Testing Savings Plan for User ID: {user.id}")
        
        # Test Case 1: Goal $5000
        goal_amount = 5000
        print(f"\n--- Analyzing Goal: ${goal_amount} ---")
        
        result = analyze_savings_plan(user.id, goal_amount)
        
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    test_savings()

from app import create_app, db
from app.models import User, MoneyScript
from app.services import calculate_persona

def test_onboarding_integration():
    app = create_app()
    with app.app_context():
        print("--- Testing Onboarding Integration ---")
        
        # 1. Create Dummy User
        # Use a unique uid to avoid conflicts
        uid = "test_onboarding_user_v1"
        user = User.query.filter_by(firebase_uid=uid).first()
        if not user:
            user = User(firebase_uid=uid, email="test_onboarding@example.com")
            db.session.add(user)
            db.session.commit()
            print(f"Created test user: {user.id}")
        else:
            print(f"Using existing test user: {user.id}")

        # 2. Simulate Input Data
        data = {
            'income': 120000,
            'age': 30,
            'quiz_answers': {'q1': 20, 'q2': 20, 'q3': 10} # Score 50 -> Balanced Strategist
        }

        # 3. Apply Logic (Replicating routes.py logic)
        # Update Demographics
        user.age = data['age']
        user.annual_income = data['income']
        
        # Derive income_level
        if user.annual_income < 50000:
            user.income_level = 'Low'
        elif user.annual_income < 150000:
            user.income_level = 'Medium'
        else:
            user.income_level = 'High'
            
        # Calculate Persona
        risk_score, primary_persona = calculate_persona(data['quiz_answers'])
        
        # Save MoneyScript
        profile = MoneyScript.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = MoneyScript(user_id=user.id)
            db.session.add(profile)
        
        profile.risk_score = risk_score
        profile.primary_persona = primary_persona
        profile.quiz_data = data['quiz_answers']
        profile.time_horizon = 'Long' if risk_score > 60 else 'Short'
        
        db.session.commit()
        
        # 4. Verify Data Persistence
        updated_user = User.query.get(user.id)
        updated_profile = MoneyScript.query.filter_by(user_id=user.id).first()
        
        print(f"User Income Level: {updated_user.income_level}")
        print(f"Profile Persona: {updated_profile.primary_persona}")
        print(f"Profile Risk Score: {updated_profile.risk_score}")
        print(f"Profile Quiz Data: {updated_profile.quiz_data}")

        assert updated_user.income_level == 'Medium'
        assert updated_profile.primary_persona == 'Balanced Strategist'
        assert updated_profile.risk_score == 50
        assert updated_profile.quiz_data == {'q1': 20, 'q2': 20, 'q3': 10}
        
        print("\nIntegration Test Passed Successfully!")

if __name__ == "__main__":
    test_onboarding_integration()

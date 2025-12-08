from app import create_app
from app.services import get_hybrid_recommendations
from app.models import User

app = create_app()

def test_engine():
    with app.app_context():
        user = User.query.filter_by(firebase_uid='test_user_123').first()
        if not user:
            print("Test user not found")
            return
            
        print(f"Testing Recommendations for User {user.id} ({user.email})...")
        recs = get_hybrid_recommendations(user.id)
        
        print("\n--- Recommendations ---")
        for r in recs:
            print(f"Product: {r['product']}")
            print(f"  Reason: {r['reason']}")
            print(f"  Score: {r['score']:.2f}")
            print(f"  Source: {r['source']}")
            print("-" * 20)

if __name__ == '__main__':
    test_engine()

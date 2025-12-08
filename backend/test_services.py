from app import create_app, db
from app.models import User
from app.services import analyze_spending, generate_chat_response
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app()

def test_services():
    with app.app_context():
        # Get the seed user
        user = User.query.filter_by(firebase_uid='test_user_123').first()
        if not user:
            print("Error: Seed user 'test_user_123' not found. Please run ingest_data.py first.")
            return

        print(f"Testing for User ID: {user.id}")

        # Test Spending Analysis
        print("\n--- Testing Spending Analysis ---")
        spending = analyze_spending(user.id)
        print("Spending Summary:", spending)

        # Test Chatbot
        print("\n--- Testing Chatbot (Gemini) ---")
        question = "How much did I spend on food?"
        print(f"Question: {question}")
        
        if not os.getenv("GEMINI_API_KEY"):
             print("Error: GEMINI_API_KEY not found in environment. Please check your .env file.")
        else:
            try:
                response = generate_chat_response(user.id, question)
                print("Response:", response)
            except Exception as e:
                print("Error generating response:", e)

if __name__ == '__main__':
    test_services()

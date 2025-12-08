from app import create_app, db
from app.models import User

app = create_app()

def check_user():
    with app.app_context():
        # UID from the log
        target_uid = "AdDYvZTWh8faXYvJPhRI6DTX3JA2"
        
        print(f"Checking for user with UID: {target_uid}")
        user = User.query.filter_by(firebase_uid=target_uid).first()
        
        if user:
            print(f"FOUND: User ID {user.id}, Email: {user.email}")
        else:
            print("NOT FOUND: User does not exist in the database.")
            
        print("\nAll Users:")
        users = User.query.all()
        for u in users:
            print(f"- ID: {u.id}, UID: {u.firebase_uid}, Email: {u.email}")

if __name__ == "__main__":
    import sys
    with open('user_check_result.txt', 'w') as f:
        sys.stdout = f
        check_user()

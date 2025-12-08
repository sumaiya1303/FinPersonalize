from app import create_app, db
from app.models import User, Transaction

app = create_app()

def reset_db():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Database reset complete.")

if __name__ == '__main__':
    reset_db()

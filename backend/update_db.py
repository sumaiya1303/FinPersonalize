from app import create_app, db
from app.models import SystemLog

app = create_app()

with app.app_context():
    db.create_all()
    print("Database schema updated: SystemLog table created.")

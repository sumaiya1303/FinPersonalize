from app import create_app, db
from app.models import User, Transaction
from sqlalchemy import func, desc
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    user = User.query.first()
    print(f"User ID: {user.id}")
    
    ninety_days_ago = datetime.utcnow() - timedelta(days=90)
    print(f"90 Days Ago: {ninety_days_ago}")
    
    # Query 1: Audit Utils Logic
    print("\n--- Audit Utils Query ---")
    top_category = db.session.query(Transaction.category, func.sum(Transaction.amount).label('total'))\
        .filter(Transaction.user_id == user.id, Transaction.amount < 0, Transaction.date >= ninety_days_ago)\
        .group_by(Transaction.category)\
        .order_by(func.sum(Transaction.amount).asc())\
        .first()
    print(f"Top Category: {top_category}")
    
    # Query 2: Services Logic
    print("\n--- Services Query ---")
    top_categories = db.session.query(
        Transaction.category, func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user.id,
        Transaction.amount < 0,
        Transaction.date >= ninety_days_ago
    ).group_by(Transaction.category).order_by(desc('total')).limit(3).all()
    
    print(f"Top 3 Categories: {top_categories}")
    
    # Dump all categories in last 90 days
    print("\n--- All Categories (Last 90 Days) ---")
    all_cats = db.session.query(Transaction.category, func.sum(Transaction.amount).label('total'))\
        .filter(Transaction.user_id == user.id, Transaction.amount < 0, Transaction.date >= ninety_days_ago)\
        .group_by(Transaction.category)\
        .order_by(func.sum(Transaction.amount).asc())\
        .all()
    for c in all_cats:
        print(f"{c.category}: {c.total}")

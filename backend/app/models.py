from . import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), nullable=True)
    risk_tolerance = db.Column(db.String(50), default='medium')
    income_level = db.Column(db.String(50), default='medium')
    age = db.Column(db.Integer, nullable=True)
    annual_income = db.Column(db.Float, nullable=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), default='General')
    vendor = db.Column(db.String(100), nullable=True)
    merchant_clean = db.Column(db.String(100), nullable=True)
    sub_category = db.Column(db.String(100), nullable=True)
    type = db.Column(db.String(20), nullable=True)  # debit/credit
    balance_after = db.Column(db.Float, nullable=True)

class MoneyScript(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    risk_score = db.Column(db.Integer, default=0)
    primary_persona = db.Column(db.String(100), nullable=True)
    time_horizon = db.Column(db.String(50), nullable=True)
    quiz_data = db.Column(db.JSON, nullable=True)

class CategoryRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), nullable=False)
    category_name = db.Column(db.String(100), nullable=False)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    risk_level = db.Column(db.String(50), nullable=True)
    tags = db.Column(db.String(255), nullable=True)

class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False) # 'chat_query', 'reco_click'
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class RecurringBill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vendor_name = db.Column(db.String(100), nullable=False)
    average_amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(50), default='Monthly')
    day_of_month = db.Column(db.Integer, nullable=False)
    last_paid_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

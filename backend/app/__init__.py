from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176"]}})
    
    # Initialize Firebase Admin
    import firebase_admin
    from firebase_admin import credentials
    
    cred_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'firebase_credentials.json')
    if os.path.exists(cred_path):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin initialized.")
    else:
        print(f"Warning: firebase_credentials.json not found at {cred_path}")

    from .routes import main
    app.register_blueprint(main)

    @app.after_request
    def add_header(response):
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
        return response

    return app

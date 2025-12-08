from functools import wraps
from flask import request, jsonify
import firebase_admin
from firebase_admin import auth

def verify_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        print(f"DEBUG: Auth Header: {auth_header}")
        if not auth_header:
            return jsonify({'error': 'Authorization header is missing'}), 401
        
        try:
            token = auth_header.split(" ")[1]
            decoded_token = auth.verify_id_token(token, clock_skew_seconds=5)
            request.user = decoded_token # Attach user info to request
        except Exception as e:
            print(f"Auth Error: {e}")
            with open("auth_error.log", "w") as log_file:
                log_file.write(f"Auth Error: {str(e)}\n")
            return jsonify({'error': 'Invalid token', 'details': str(e)}), 401
            
        return f(*args, **kwargs)
            
    return decorated_function

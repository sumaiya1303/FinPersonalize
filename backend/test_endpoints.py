import requests
import sys
from get_id_token import get_id_token
import firebase_admin
from firebase_admin import auth, credentials
import os
import re

# We need to replicate get_id_token logic to return the token string instead of just printing it
# Or we can just import it if we refactor get_id_token. 
# For speed, I'll just copy the token generation logic here or modify get_id_token to return it.

def generate_token():
    # Initialize Firebase Admin if needed
    if not firebase_admin._apps:
        cred_path = os.path.join(os.path.dirname(__file__), 'firebase_credentials.json')
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            
    uid = 'test_user_123'
    try:
        custom_token = auth.create_custom_token(uid)
    except Exception as e:
        print(f"Error creating custom token: {e}")
        return None

    # Get API Key
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("FIREBASE_WEB_API_KEY")
    
    if not api_key:
        print("Could not find FIREBASE_WEB_API_KEY in .env")
        return None

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}"
    payload = {
        "token": custom_token.decode('utf-8') if isinstance(custom_token, bytes) else custom_token,
        "returnSecureToken": True
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()['idToken']
    else:
        print(f"Error exchanging token: {response.text}")
        return None

def test_endpoints():
    print("Generating Token...")
    token = generate_token()
    if not token:
        return

    base_url = "http://localhost:5000/api"
    headers = {"Authorization": f"Bearer {token}"}

    print("\n1. Testing /api/sync-user...")
    try:
        res = requests.post(f"{base_url}/sync-user", headers=headers)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"Failed: {e}")

    print("\n2. Testing /api/transactions...")
    try:
        res = requests.get(f"{base_url}/transactions", headers=headers)
        print(f"Status: {res.status_code}")
        data = res.json()
        print(f"Got {len(data)} transactions.")
        if data:
            print(f"Sample: {data[0]}")
    except Exception as e:
        print(f"Failed: {e}")

    print("\n3. Testing /api/analysis...")
    try:
        res = requests.get(f"{base_url}/analysis", headers=headers)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"Failed: {e}")

    print("\n4. Testing /api/chat...")
    try:
        res = requests.post(f"{base_url}/chat", headers=headers, json={"message": "How much on food?"})
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == '__main__':
    test_endpoints()

import firebase_admin
from firebase_admin import credentials, auth
import requests
import os
import json

# Initialize Firebase Admin if not already initialized
if not firebase_admin._apps:
    cred_path = os.path.join(os.path.dirname(__file__), 'firebase_credentials.json')
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        print(f"Error: firebase_credentials.json not found at {cred_path}")
        exit(1)

def get_id_token():
    uid = 'test_user_123'
    
    print(f"Generating custom token for UID: {uid}...")
    try:
        custom_token = auth.create_custom_token(uid)
    except Exception as e:
        print(f"Error creating custom token: {e}")
        return

    # To exchange custom token for ID token, we need the Web API Key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("FIREBASE_WEB_API_KEY")
    
    if not api_key:
        api_key = input("\nEnter your Firebase Web API Key: ").strip()
    
    if not api_key:
        print("API Key is required.")
        return

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}"
    
    payload = {
        "token": custom_token.decode('utf-8') if isinstance(custom_token, bytes) else custom_token,
        "returnSecureToken": True
    }
    
    print("\nExchanging custom token for ID token...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        id_token = data['idToken']
        print("\nSUCCESS! Here is your ID Token:\n")
        print(id_token)
        print("\n--- Usage ---")
        print(f"curl -X GET http://localhost:5000/api/transactions -H \"Authorization: Bearer {id_token}\"")
    else:
        print(f"\nError exchanging token: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    get_id_token()

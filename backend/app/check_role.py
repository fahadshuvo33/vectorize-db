# backend/check_role.py
import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()

def get_role(token_name, token):
    if not token:
        print(f"{token_name}: [Empty]")
        return
    
    try:
        # JWT is Header.Payload.Signature. We want Payload (index 1).
        parts = token.split('.')
        payload = parts[1]
        # Fix Base64 padding
        payload += '=' * (-len(payload) % 4)
        
        decoded_bytes = base64.b64decode(payload)
        data = json.loads(decoded_bytes)
        role = data.get("role", "No role found")
        
        print(f"{token_name} Internal Role: --> {role} <--")
    except Exception as e:
        print(f"{token_name}: Error decoding: {e}")

print("--- CHECKING TOKEN ROLES ---")
get_role("ANON_KEY", os.getenv("SUPABASE_KEY"))
get_role("SERVICE_KEY", os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
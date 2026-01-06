# backend/check_keys.py
import os
from supabase import create_client
from dotenv import load_dotenv

# Force load the .env file
load_dotenv()

URL = os.getenv("SUPABASE_URL")
ANON_KEY = os.getenv("SUPABASE_KEY")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("\n--- KEY DIAGNOSTICS ---")
print(f"URL: {URL}")
print(f"ANON KEY (First 10):    {ANON_KEY[:10]}...")
print(f"SERVICE KEY (First 10): {SERVICE_KEY[:10]}...")

if ANON_KEY == SERVICE_KEY:
    print("\n❌ CRITICAL ERROR: Your Service Key is IDENTICAL to your Anon Key.")
    print("   Please go to Supabase > Project Settings > API and copy the 'service_role' key.")
else:
    print("\n✅ Keys are different. Testing connection...")

    # Test Anon
    try:
        print("\nTesting ANON Key (Should fail or return 0 if RLS blocks)...")
        client = create_client(URL, ANON_KEY)
        client.table("profiles").select("*").limit(1).execute()
        print("   -> Anon Connection: OK")
    except Exception as e:
        print(f"   -> Anon Connection Result: {e}")

    # Test Service
    try:
        print("\nTesting SERVICE Key (Should SUCCEED and bypass RLS)...")
        admin = create_client(URL, SERVICE_KEY)
        # This is the line failing in your app
        resp = admin.table("profiles").select("*").limit(1).execute() 
        print("   -> Service Connection: SUCCESS! ✅")
    except Exception as e:
        print(f"   -> Service Connection FAILED: {e}")
        print("   ❌ This means the key you put in SUPABASE_SERVICE_ROLE_KEY is NOT an admin key.")
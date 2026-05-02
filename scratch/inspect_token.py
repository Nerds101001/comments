
import asyncio
import os
import sys
import json
import base64
from dotenv import load_dotenv

# Add the project root to sys.path
sys.path.append(os.path.abspath("."))
load_dotenv()

from app.services import crm_client

async def inspect_token():
    print("--- CRM TOKEN INSPECTION ---")
    token = await crm_client._get_token()
    print(f"Token: {token[:20]}...")
    
    try:
        # Decode JWT payload
        header, payload, signature = token.split('.')
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.b64decode(payload).decode('utf-8')
        data = json.loads(decoded)
        print(f"Decoded Payload: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Failed to decode token: {e}")

    # Try to fetch current user info
    print("\nTrying to find current user details...")
    try:
        # Some CRM APIs have a /me or /profile or /GetCurrentUser
        me = await crm_client._get("/api/User/GetCurrentUser")
        print(f"GetCurrentUser: {me}")
    except:
        pass

if __name__ == "__main__":
    asyncio.run(inspect_token())

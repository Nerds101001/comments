#!/usr/bin/env python3
"""
Detailed WhatsApp Token Diagnostics
"""
import asyncio
import aiohttp
from app.config import settings

async def diagnose_token():
    print("=" * 100)
    print("WHATSAPP TOKEN DIAGNOSTICS")
    print("=" * 100)
    
    token = settings.WHATSAPP_ACCESS_TOKEN
    phone_id = settings.WHATSAPP_PHONE_NUMBER_ID
    
    print("\n1. TOKEN INFORMATION:")
    print(f"   Length: {len(token)} characters")
    print(f"   Starts with: {token[:10]}")
    print(f"   Ends with: {token[-10:]}")
    print(f"   Full token: {token}")
    
    print("\n2. PHONE NUMBER ID:")
    print(f"   {phone_id}")
    
    # Test 1: Check if we can access the phone number details
    print("\n3. TESTING: Get Phone Number Details...")
    url = f"https://graph.facebook.com/v20.0/{phone_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Response: {data}")
                
                if resp.status == 200:
                    print("\n   ✅ Token can access phone number!")
                    print(f"   Verified Name: {data.get('verified_name', 'N/A')}")
                    print(f"   Display Phone: {data.get('display_phone_number', 'N/A')}")
                else:
                    print(f"\n   ❌ Error accessing phone number")
                    if "error" in data:
                        print(f"   Error Code: {data['error'].get('code')}")
                        print(f"   Error Message: {data['error'].get('message')}")
                        print(f"   Error Type: {data['error'].get('type')}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test 2: Check token permissions
    print("\n4. TESTING: Token Debug Info...")
    debug_url = f"https://graph.facebook.com/v20.0/debug_token"
    params = {
        "input_token": token,
        "access_token": token
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(debug_url, params=params) as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Response: {data}")
                
                if resp.status == 200 and "data" in data:
                    token_data = data["data"]
                    print("\n   TOKEN DETAILS:")
                    print(f"   App ID: {token_data.get('app_id', 'N/A')}")
                    print(f"   Type: {token_data.get('type', 'N/A')}")
                    print(f"   Valid: {token_data.get('is_valid', False)}")
                    print(f"   Expires: {token_data.get('expires_at', 'Never')}")
                    print(f"   Scopes: {token_data.get('scopes', [])}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test 3: Try to send a test message
    print("\n5. TESTING: Send Message...")
    send_url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": settings.MUKUL_PHONE,
        "type": "text",
        "text": {"body": "Test from diagnostic script"}
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(send_url, headers=headers, json=payload) as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Response: {data}")
                
                if resp.status == 200:
                    print("\n   ✅ Message sent successfully!")
                else:
                    print(f"\n   ❌ Failed to send message")
                    if "error" in data:
                        error = data["error"]
                        print(f"\n   ERROR DETAILS:")
                        print(f"   Code: {error.get('code')}")
                        print(f"   Message: {error.get('message')}")
                        print(f"   Type: {error.get('type')}")
                        print(f"   Trace ID: {error.get('fbtrace_id')}")
                        
                        # Provide specific guidance based on error code
                        code = error.get('code')
                        if code == 190:
                            print("\n   SOLUTION FOR ERROR 190:")
                            print("   This means the access token is invalid, expired, or malformed.")
                            print("\n   Please generate a NEW token:")
                            print("   1. Go to: https://developers.facebook.com/apps/974929091900005/whatsapp-business/wa-dev-console/")
                            print("   2. Click 'Generate Access Token' button")
                            print("   3. Copy the ENTIRE token (should be 200-300 characters)")
                            print("   4. Update .env file with the new token")
                            print("\n   OR for a permanent token:")
                            print("   1. Go to: https://business.facebook.com/settings/system-users")
                            print("   2. Create a System User")
                            print("   3. Generate a permanent token with whatsapp_business_messaging permission")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 100)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 100)

if __name__ == "__main__":
    asyncio.run(diagnose_token())

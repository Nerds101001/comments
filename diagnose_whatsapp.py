#!/usr/bin/env python3
"""
Diagnose WhatsApp Business API configuration
"""
import asyncio
import httpx
from app.config import settings

async def diagnose():
    print("=" * 100)
    print("WHATSAPP BUSINESS API DIAGNOSTICS")
    print("=" * 100)
    
    print("\n1. Configuration Check:")
    print(f"   Phone Number ID: {settings.WHATSAPP_PHONE_NUMBER_ID}")
    print(f"   API Version: {settings.WHATSAPP_API_VERSION}")
    print(f"   Token (first 30 chars): {settings.WHATSAPP_ACCESS_TOKEN[:30]}...")
    print(f"   Token length: {len(settings.WHATSAPP_ACCESS_TOKEN)} characters")
    
    # Test 1: Verify token is valid
    print("\n2. Testing Access Token...")
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            # Try to get account info
            url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/me"
            headers = {"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"}
            
            resp = await client.get(url, headers=headers)
            print(f"   Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"   ✅ Token is valid!")
                print(f"   App ID: {data.get('id', 'N/A')}")
                print(f"   App Name: {data.get('name', 'N/A')}")
            else:
                print(f"   ❌ Token validation failed")
                print(f"   Response: {resp.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Check phone number ID
    print("\n3. Testing Phone Number ID...")
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}"
            headers = {"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"}
            
            resp = await client.get(url, headers=headers)
            print(f"   Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"   ✅ Phone Number ID is valid!")
                print(f"   Display Phone: {data.get('display_phone_number', 'N/A')}")
                print(f"   Verified Name: {data.get('verified_name', 'N/A')}")
                print(f"   Quality Rating: {data.get('quality_rating', 'N/A')}")
            else:
                print(f"   ❌ Phone Number ID validation failed")
                error = resp.json()
                print(f"   Response: {error}")
                
                if error.get('error', {}).get('code') == 190:
                    print("\n   💡 ISSUE FOUND: Token doesn't have access to this Phone Number ID")
                    print("   SOLUTION:")
                    print("   1. Go to Meta Business Manager")
                    print("   2. Verify the token is for the correct WhatsApp Business Account")
                    print("   3. Ensure the Phone Number ID belongs to the same account")
                    print("   4. Generate a new token with proper permissions")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: List available phone numbers
    print("\n4. Checking Available Phone Numbers...")
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            # Try to get WABA ID first
            url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/me/accounts"
            headers = {"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"}
            
            resp = await client.get(url, headers=headers)
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"   ✅ Found {len(data.get('data', []))} accounts")
                
                for account in data.get('data', []):
                    print(f"\n   Account: {account.get('name', 'N/A')}")
                    print(f"   ID: {account.get('id', 'N/A')}")
                    
                    # Try to get phone numbers for this account
                    waba_id = account.get('id')
                    phone_url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{waba_id}/phone_numbers"
                    phone_resp = await client.get(phone_url, headers=headers)
                    
                    if phone_resp.status_code == 200:
                        phone_data = phone_resp.json()
                        for phone in phone_data.get('data', []):
                            print(f"   📱 Phone: {phone.get('display_phone_number', 'N/A')}")
                            print(f"      ID: {phone.get('id', 'N/A')}")
                            print(f"      Verified: {phone.get('verified_name', 'N/A')}")
                            
                            if phone.get('id') == settings.WHATSAPP_PHONE_NUMBER_ID:
                                print(f"      ✅ THIS IS YOUR CONFIGURED PHONE NUMBER!")
            else:
                print(f"   ⚠️  Could not list accounts")
                print(f"   Response: {resp.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 100)
    print("DIAGNOSIS COMPLETE")
    print("=" * 100)
    
    print("\n📋 RECOMMENDATIONS:")
    print("1. If token is invalid: Generate a new System User token from Meta Business Manager")
    print("2. If Phone Number ID mismatch: Use the correct Phone Number ID from the list above")
    print("3. If no accounts found: Verify the token has 'whatsapp_business_management' permission")
    print("4. If still failing: Check Meta Business Manager for account restrictions")
    print("\n🔗 Useful Links:")
    print("   • Business Manager: https://business.facebook.com/")
    print("   • System Users: https://business.facebook.com/settings/system-users")
    print("   • WhatsApp Manager: https://business.facebook.com/wa/manage/home/")
    print("=" * 100)

if __name__ == "__main__":
    asyncio.run(diagnose())

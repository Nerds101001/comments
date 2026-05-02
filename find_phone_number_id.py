#!/usr/bin/env python3
"""
Find the correct WhatsApp Phone Number ID for your token
"""
import requests
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("WHATSAPP_ACCESS_TOKEN")
app_id = "974929091900005"  # Your app ID

print("=" * 100)
print("FINDING CORRECT WHATSAPP PHONE NUMBER ID")
print("=" * 100)

print(f"\n1. Your App ID: {app_id}")
print(f"2. Current Phone Number ID in .env: 114125338435757")
print(f"3. Token length: {len(token)} characters")

# Try to get WhatsApp Business Account ID
print("\n4. STEP 1: Getting WhatsApp Business Account ID...")
url = f"https://graph.facebook.com/v20.0/{app_id}"
params = {
    "fields": "whatsapp_business_account",
    "access_token": token
}

try:
    response = requests.get(url, params=params)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response: {data}")
    
    if response.status_code == 200:
        if "whatsapp_business_account" in data:
            waba_id = data["whatsapp_business_account"]["id"]
            print(f"\n   ✅ Found WhatsApp Business Account ID: {waba_id}")
            
            # Now get phone numbers for this WABA
            print("\n5. STEP 2: Getting Phone Numbers for this account...")
            phone_url = f"https://graph.facebook.com/v20.0/{waba_id}/phone_numbers"
            params = {"access_token": token}
            
            phone_response = requests.get(phone_url, params=params)
            print(f"   Status: {phone_response.status_code}")
            phone_data = phone_response.json()
            print(f"   Response: {phone_data}")
            
            if phone_response.status_code == 200 and "data" in phone_data:
                print("\n   ✅ FOUND PHONE NUMBERS:")
                for phone in phone_data["data"]:
                    print(f"\n   Phone Number: {phone.get('display_phone_number')}")
                    print(f"   Phone Number ID: {phone.get('id')}")
                    print(f"   Verified Name: {phone.get('verified_name')}")
                    print(f"   Quality Rating: {phone.get('quality_rating')}")
                    
                if phone_data["data"]:
                    correct_id = phone_data["data"][0]["id"]
                    print("\n" + "=" * 100)
                    print("✅ SUCCESS! Found your Phone Number ID")
                    print("=" * 100)
                    print(f"\nYour CORRECT Phone Number ID is: {correct_id}")
                    print(f"\nUpdate your .env file:")
                    print(f"WHATSAPP_PHONE_NUMBER_ID={correct_id}")
                    print("\nI'll update it for you now...")
                    print("=" * 100)
                else:
                    print("\n   ⚠️ No phone numbers found for this account")
                    print("   You need to add a phone number in the WhatsApp Business console")
            else:
                print(f"\n   ❌ Could not get phone numbers")
        else:
            print("\n   ⚠️ No WhatsApp Business Account linked to this app")
            print("   Please link a WhatsApp Business Account in the developer console")
    else:
        print(f"\n   ❌ Could not access app details")
        if "error" in data:
            print(f"   Error: {data['error'].get('message')}")
            
except Exception as e:
    print(f"\n   ❌ Exception: {e}")

# Alternative: Try to list all accessible WhatsApp Business Accounts
print("\n6. ALTERNATIVE: Trying to list all accessible accounts...")
me_url = "https://graph.facebook.com/v20.0/me/accounts"
params = {"access_token": token}

try:
    response = requests.get(me_url, params=params)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response: {data}")
except Exception as e:
    print(f"   Exception: {e}")

print("\n" + "=" * 100)
print("DIAGNOSTIC COMPLETE")
print("=" * 100)
print("\nIf no phone number was found, you need to:")
print("1. Go to: https://developers.facebook.com/apps/974929091900005/whatsapp-business/wa-dev-console/")
print("2. Make sure a phone number is added and verified")
print("3. Generate a NEW token from that same page")
print("4. The token must be generated from the SAME page where your phone number is shown")
print("=" * 100)

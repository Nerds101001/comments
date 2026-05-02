#!/usr/bin/env python3
"""
Check WhatsApp message delivery status and troubleshoot
"""
import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()

token = os.getenv("WHATSAPP_ACCESS_TOKEN")
phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
test_number = "917889041267"

print("=" * 100)
print("CHECKING WHATSAPP MESSAGE STATUS")
print("=" * 100)

# First, let's verify the phone number details
print("\n1. CHECKING PHONE NUMBER CONFIGURATION...")
phone_url = f"https://graph.facebook.com/v20.0/{phone_id}"
headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get(phone_url, headers=headers)
    data = response.json()
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ Verified Name: {data.get('verified_name')}")
        print(f"   ✅ Display Phone: {data.get('display_phone_number')}")
        print(f"   ✅ Quality Rating: {data.get('quality_rating')}")
        print(f"   ✅ Code Verification: {data.get('code_verification_status')}")
        
        # Check if phone is verified
        if data.get('code_verification_status') == 'NOT_VERIFIED':
            print("\n   ⚠️ WARNING: Phone number is NOT_VERIFIED")
            print("   This might prevent message delivery!")
            print("\n   TO FIX:")
            print("   1. Go to wa-dev-console")
            print("   2. Verify your phone number with the code")
            print("   3. Complete the verification process")
    else:
        print(f"   ❌ Error: {data}")
        
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Check if we can get message templates
print("\n2. CHECKING AVAILABLE MESSAGE TEMPLATES...")
template_url = f"https://graph.facebook.com/v20.0/{phone_id}/message_templates"
params = {"access_token": token}

try:
    response = requests.get(template_url, params=params)
    data = response.json()
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200 and "data" in data:
        templates = data["data"]
        print(f"   ✅ Found {len(templates)} templates")
        for template in templates:
            print(f"      - {template.get('name')} ({template.get('status')})")
    else:
        print(f"   Response: {data}")
        
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Try sending with the hello_world template
print("\n3. TRYING TO SEND HELLO_WORLD TEMPLATE...")
send_url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "messaging_product": "whatsapp",
    "to": test_number,
    "type": "template",
    "template": {
        "name": "hello_world",
        "language": {
            "code": "en_US"
        }
    }
}

try:
    response = requests.post(send_url, headers=headers, json=payload)
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Response: {data}")
    
    if response.status_code == 200:
        print("\n   ✅ Template message sent!")
        if "messages" in data:
            msg_id = data["messages"][0].get("id")
            print(f"   Message ID: {msg_id}")
            print("\n   📱 Check +917889041267 for 'Hello World' message")
    else:
        error = data.get("error", {})
        print(f"\n   ❌ Error: {error.get('message')}")
        print(f"   Code: {error.get('code')}")
        
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Check webhook configuration
print("\n4. CHECKING WEBHOOK CONFIGURATION...")
webhook_url = f"https://graph.facebook.com/v20.0/{phone_id}/subscribed_apps"
params = {"access_token": token}

try:
    response = requests.get(webhook_url, params=params)
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Response: {data}")
    
except Exception as e:
    print(f"   ❌ Exception: {e}")

print("\n" + "=" * 100)
print("DIAGNOSTIC SUMMARY")
print("=" * 100)

print("\n⚠️ POSSIBLE REASONS WHY MESSAGE WASN'T RECEIVED:")
print("\n1. PHONE NUMBER NOT VERIFIED:")
print("   - Your sender phone number might not be verified")
print("   - Go to wa-dev-console and complete verification")

print("\n2. RECIPIENT NUMBER FORMAT:")
print("   - Make sure +917889041267 is the correct format")
print("   - Should be: country code + number (no + sign in API)")

print("\n3. WHATSAPP NOT INSTALLED:")
print("   - Recipient must have WhatsApp installed")
print("   - Number must be registered on WhatsApp")

print("\n4. 24-HOUR WINDOW:")
print("   - In dev mode, you can only send templates")
print("   - Custom messages need prior conversation")
print("   - Or number must be in allowed list AND verified")

print("\n5. MESSAGE QUEUE DELAY:")
print("   - Sometimes messages take 1-2 minutes")
print("   - Check WhatsApp again in a few minutes")

print("\n" + "=" * 100)
print("RECOMMENDED ACTIONS:")
print("=" * 100)

print("\n1. Verify your sender phone number in wa-dev-console")
print("2. Confirm +917889041267 has WhatsApp installed")
print("3. Try the hello_world template (sent above)")
print("4. Wait 2-3 minutes and check WhatsApp again")
print("5. Check if you received any error notifications in Meta Business Suite")

print("\n" + "=" * 100)

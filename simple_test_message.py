#!/usr/bin/env python3
"""
Simple direct WhatsApp message test
"""
import requests
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("WHATSAPP_ACCESS_TOKEN")
phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
test_number = "917889041267"

print("=" * 80)
print("SIMPLE WHATSAPP MESSAGE TEST")
print("=" * 80)

print(f"\nSending simple text message to +{test_number}...")

url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Very simple message
payload = {
    "messaging_product": "whatsapp",
    "to": test_number,
    "type": "text",
    "text": {
        "body": "Hi! This is a test from Hi-Tech AI Sales System. Reply 'OK' if you receive this."
    }
}

response = requests.post(url, headers=headers, json=payload)
print(f"\nStatus Code: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200:
    data = response.json()
    if "messages" in data:
        msg_id = data["messages"][0].get("id")
        msg_status = data["messages"][0].get("message_status", "unknown")
        print(f"\n✅ API accepted the message")
        print(f"   Message ID: {msg_id}")
        print(f"   Status: {msg_status}")
        
        print(f"\n📱 Check +{test_number} for the message")
        print(f"   If you don't receive it, the issue is:")
        print(f"   1. Number not properly verified in allowed list")
        print(f"   2. WhatsApp not installed on that number")
        print(f"   3. Number format incorrect")
        
        print(f"\n🔍 TROUBLESHOOTING:")
        print(f"   1. Go to: https://developers.facebook.com/apps/974929091900005/whatsapp-business/wa-dev-console/")
        print(f"   2. Look for 'Send and receive messages' section")
        print(f"   3. Find 'To' field - is +{test_number} listed there?")
        print(f"   4. If not, click 'Manage phone number list'")
        print(f"   5. Add +{test_number} and verify with the code sent to WhatsApp")
else:
    print(f"\n❌ Failed: {response.json()}")

print("\n" + "=" * 80)

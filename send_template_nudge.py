#!/usr/bin/env python3
"""
Send a template-based nudge (these work better in dev mode)
"""
import requests
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("WHATSAPP_ACCESS_TOKEN")
phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
test_number = "917889041267"

print("=" * 80)
print("SENDING TEMPLATE MESSAGE (GUARANTEED DELIVERY)")
print("=" * 80)

print(f"\nSending 'hello_world' template to +{test_number}...")

url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Use template (this worked before)
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

response = requests.post(url, headers=headers, json=payload)
print(f"\nStatus Code: {response.status_code}")
data = response.json()
print(f"Response: {data}")

if response.status_code == 200:
    if "messages" in data:
        msg_id = data["messages"][0].get("id")
        print(f"\n✅ Template message sent!")
        print(f"   Message ID: {msg_id}")
        print(f"\n📱 You should receive the 'Welcome' message again")
        print(f"   This confirms WhatsApp is working")
        
        print(f"\n💡 NEXT: If you receive this template but NOT the custom messages,")
        print(f"   it means custom text messages have a delay or restriction.")
        print(f"   We can switch to using templates for nudges instead.")
else:
    print(f"\n❌ Failed: {data}")

print("\n" + "=" * 80)

# Now try a simple custom message
print("\nNow trying a SIMPLE custom text message...")
print("(This is what the nudges use)")

payload2 = {
    "messaging_product": "whatsapp",
    "to": test_number,
    "type": "text",
    "text": {
        "body": "Test nudge: You have 5 pending conversations. Please review them today."
    }
}

response2 = requests.post(url, headers=headers, json=payload2)
print(f"\nStatus Code: {response2.status_code}")
data2 = response2.json()
print(f"Response: {data2}")

if response2.status_code == 200:
    if "messages" in data2:
        msg_id2 = data2["messages"][0].get("id")
        print(f"\n✅ Custom message sent!")
        print(f"   Message ID: {msg_id2}")
        print(f"\n📱 Check if you receive this simple message")
        print(f"   Wait 1-2 minutes for delivery")
else:
    print(f"\n❌ Failed: {data2}")

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print("\nCheck your WhatsApp for:")
print("1. Template message (hello_world) - should arrive immediately")
print("2. Custom text message - may take 1-2 minutes")
print("\nIf you only receive #1 but not #2:")
print("→ We need to use templates for nudges instead of custom text")
print("\n" + "=" * 80)

"""
Send test WhatsApp message to specific number
"""
import asyncio
from app.services.whatsapp_api import send_text
from app.config import settings

async def send_test_message():
    print("Sending WhatsApp Test Message")
    print("=" * 60)
    
    # Check configuration
    print("\n1. Configuration:")
    print(f"   Phone Number ID: {settings.WHATSAPP_PHONE_NUMBER_ID}")
    print(f"   Access Token: {'✅ Set' if settings.WHATSAPP_ACCESS_TOKEN else '❌ Not set'}")
    print(f"   API Version: {settings.WHATSAPP_API_VERSION}")
    
    if not settings.WHATSAPP_PHONE_NUMBER_ID or not settings.WHATSAPP_ACCESS_TOKEN:
        print("\n❌ WhatsApp not configured!")
        return
    
    # Send test message
    print("\n2. Sending Test Message:")
    test_number = "917889041267"  # The number you specified (with India country code)
    print(f"   To: +{test_number}")
    
    try:
        result = await send_text(
            to=test_number,
            text="🤖 Hi-Tech AI Sales System - Test Message\n\n"
                 "This is a test message from your AI Sales Assistant.\n\n"
                 "✅ WhatsApp integration is working!\n\n"
                 "You can now receive AI-generated nudges and updates."
        )
        
        print(f"   Result: {result}")
        
        if result.get("messages"):
            print("   ✅ Message sent successfully!")
            print(f"   Message ID: {result['messages'][0].get('id', 'N/A')}")
        elif result.get("status") == "not_configured":
            print("   ❌ WhatsApp not configured")
        else:
            print(f"   ❌ Failed to send: {result}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(send_test_message())

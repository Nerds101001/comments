# 📱 WhatsApp Business API Setup Guide

## ✅ Configuration Added

Your WhatsApp credentials have been added to `.env`:

```env
WHATSAPP_PHONE_NUMBER_ID=114125338435757
WHATSAPP_ACCESS_TOKEN=EAAN2sV40MmU... (configured)
WHATSAPP_VERIFY_TOKEN=hitech-verify-2026
WHATSAPP_API_VERSION=v20.0
MUKUL_PHONE=918264409000
```

---

## ⚠️ ACCESS TOKEN ISSUE

The test shows an **Authentication Error (Code 190)**. This means:

### Possible Causes:
1. **Token Expired** - Access tokens expire after 24-60 days
2. **Token Invalid** - Token may have been regenerated
3. **Permissions Changed** - App permissions may have been modified
4. **Account Issue** - WhatsApp Business account may need verification

---

## 🔧 HOW TO FIX

### Option 1: Generate New Permanent Access Token (Recommended)

1. **Go to Meta Business Manager**
   - Visit: https://business.facebook.com/settings/system-users
   
2. **Create/Select System User**
   - Click "Add" → Create new system user
   - Name: "Hi-Tech AI Sales Bot"
   - Role: Admin

3. **Generate Token**
   - Click on the system user
   - Click "Generate New Token"
   - Select your WhatsApp app: "Hi-Tech AI Sales"
   - Select permissions:
     - ✅ `whatsapp_business_messaging`
     - ✅ `whatsapp_business_management`
   - Token expiration: **Never** (permanent)
   - Click "Generate Token"

4. **Copy Token**
   - Copy the new token (starts with `EAAB...`)
   - Update `.env` file:
     ```env
     WHATSAPP_ACCESS_TOKEN=<your_new_token_here>
     ```

5. **Test Again**
   ```bash
   python test_whatsapp_setup.py
   ```

### Option 2: Use Temporary Token (Quick Test)

1. **Go to WhatsApp App Dashboard**
   - Visit: https://developers.facebook.com/apps/974929091900005/whatsapp-business/wa-dev-console/
   
2. **Get Temporary Token**
   - Click on "API Setup" tab
   - Copy the "Temporary access token" (valid for 24 hours)
   - Update `.env` with this token

3. **Test**
   ```bash
   python test_whatsapp_setup.py
   ```

**Note**: Temporary tokens expire in 24 hours. Use Option 1 for production.

---

## 📋 VERIFICATION CHECKLIST

Before testing, verify:

### 1. WhatsApp Business Account
- [ ] Account is verified
- [ ] Phone number (+91 82644 09000) is registered
- [ ] Business profile is complete

### 2. Meta App Settings
- [ ] App ID: 974929091900005
- [ ] App is in "Live" mode (not Development)
- [ ] WhatsApp product is added
- [ ] Phone Number ID: 114125338435757

### 3. Permissions
- [ ] `whatsapp_business_messaging` - Send messages
- [ ] `whatsapp_business_management` - Manage account

### 4. Message Templates (Optional)
- [ ] At least one approved template (for first message to new contacts)
- [ ] Or use "24-hour window" (reply to customer message within 24h)

---

## 🧪 TESTING

### Test 1: Send to Yourself
```bash
python test_whatsapp_setup.py
```

Expected output:
```
✅ Message sent successfully!
   Message ID: wamid.xxx...
```

### Test 2: Send to a Rep
```python
import asyncio
from app.services.whatsapp_api import send_text

async def test_rep():
    # Send to Vishal Patil
    result = await send_text(
        to="917087018419",  # Vishal's number
        text="Hi Vishal! This is a test message from Hi-Tech AI Sales system."
    )
    print(result)

asyncio.run(test_rep())
```

### Test 3: Check Webhook
```bash
# Your webhook URL should be:
https://yourdomain.com/api/whatsapp/webhook

# Test verification:
curl "https://yourdomain.com/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=hitech-verify-2026&hub.challenge=test123"

# Should return: test123
```

---

## 🚀 ONCE WORKING

### 1. Update Frontend to Send Messages

The frontend already has the structure. Just ensure the WhatsApp links work:

```html
<!-- In frontend/index.html -->
<div class="msg-actions">
  <button onclick="sendViaWhatsApp('${conv.id}', ${idx})" 
          class="btn btn-success btn-sm">
    📱 Send via WhatsApp
  </button>
</div>

<script>
async function sendViaWhatsApp(convId, msgIdx) {
  const conv = conversations.find(c => c.id === convId);
  const msg = conv.messages[msgIdx];
  const rep = REPS[conv.rep_id];
  
  // Option 1: Click-to-send (opens WhatsApp)
  const url = `https://wa.me/91${rep.phone}?text=${encodeURIComponent(msg.text)}`;
  window.open(url, '_blank');
  
  // Option 2: Send via API (automated)
  const response = await fetch('/api/whatsapp/send', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      to: rep.phone,
      message: msg.text,
      conversation_id: convId
    })
  });
  
  if (response.ok) {
    alert('Message sent via WhatsApp!');
    markSent(convId, msgIdx);
  }
}
</script>
```

### 2. Add Backend Endpoint

```python
# app/api/whatsapp.py
from fastapi import APIRouter, HTTPException
from app.services.whatsapp_api import send_text
from pydantic import BaseModel

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])

class SendMessageRequest(BaseModel):
    to: str
    message: str
    conversation_id: str = None

@router.post("/send")
async def send_whatsapp_message(req: SendMessageRequest):
    """Send a WhatsApp message to a rep"""
    try:
        # Normalize phone number
        phone = req.to.replace(' ', '').replace('-', '').replace('+', '')
        if not phone.startswith('91') and len(phone) == 10:
            phone = '91' + phone
        
        # Send message
        result = await send_text(to=phone, text=req.message)
        
        # TODO: Update conversation status in database
        # if req.conversation_id:
        #     update_message_status(req.conversation_id, 'sent')
        
        return {
            "success": True,
            "message_id": result.get("messages", [{}])[0].get("id"),
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Register the Router

```python
# app/main.py
from app.api import whatsapp

app.include_router(whatsapp.router)
```

---

## 📊 MONITORING

### Check Message Status

```python
# Get message delivery status
import httpx

async def check_message_status(message_id):
    url = f"https://graph.facebook.com/v20.0/{message_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        return resp.json()
```

### Webhook Events

When a rep replies, you'll receive a webhook POST:

```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "919812345001",
          "id": "wamid.xxx",
          "timestamp": "1234567890",
          "text": {"body": "Rep's reply here"},
          "type": "text"
        }],
        "contacts": [{
          "profile": {"name": "Vishal Patil"},
          "wa_id": "919812345001"
        }]
      }
    }]
  }]
}
```

---

## 🔐 SECURITY

### Protect Your Token

1. **Never commit `.env` to git**
   ```bash
   # .gitignore already includes:
   .env
   .env.local
   ```

2. **Use environment variables in production**
   ```bash
   # On server:
   export WHATSAPP_ACCESS_TOKEN="your_token_here"
   ```

3. **Rotate tokens regularly**
   - Generate new token every 60 days
   - Update `.env` file
   - Restart server

### Webhook Security

```python
# Verify webhook signature (optional but recommended)
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str, app_secret: str) -> bool:
    expected = hmac.new(
        app_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## 📈 RATE LIMITS

WhatsApp Business API has rate limits:

- **Tier 1** (new accounts): 1,000 messages/day
- **Tier 2**: 10,000 messages/day
- **Tier 3**: 100,000 messages/day
- **Tier 4**: Unlimited

Your tier increases automatically based on:
- Message quality (low block rate)
- Phone number verification
- Business verification

---

## 🆘 TROUBLESHOOTING

### Error 190: Authentication Error
- **Fix**: Generate new access token (see Option 1 above)

### Error 131026: Message Undeliverable
- **Cause**: Recipient hasn't messaged you first
- **Fix**: Use approved message template OR wait for rep to message you

### Error 131047: Re-engagement Message
- **Cause**: 24-hour window expired
- **Fix**: Use approved template to re-engage

### Error 131051: Unsupported Message Type
- **Cause**: Trying to send unsupported content
- **Fix**: Stick to text messages for now

### Error 133016: Rate Limit
- **Cause**: Too many messages sent
- **Fix**: Implement rate limiting, upgrade tier

---

## 📚 RESOURCES

- **Meta WhatsApp Docs**: https://developers.facebook.com/docs/whatsapp/cloud-api
- **API Reference**: https://developers.facebook.com/docs/whatsapp/cloud-api/reference
- **Business Manager**: https://business.facebook.com/
- **App Dashboard**: https://developers.facebook.com/apps/974929091900005/
- **Message Templates**: https://business.facebook.com/wa/manage/message-templates/

---

## ✅ NEXT STEPS

1. **Generate New Permanent Token** (see Option 1 above)
2. **Update `.env`** with new token
3. **Run Test**: `python test_whatsapp_setup.py`
4. **Verify Success**: Check your WhatsApp for test message
5. **Start Sending**: Use the system to send AI nudges to reps!

---

## 📞 SUPPORT

If you continue to have issues:

1. Check Meta Business Manager for account status
2. Verify phone number is registered and verified
3. Ensure app is in "Live" mode (not Development)
4. Check for any restrictions or warnings in Meta dashboard
5. Contact Meta support if needed

---

**Status**: ⚠️ Configured but needs new access token  
**Action Required**: Generate permanent access token from Meta Business Manager  
**ETA**: 5-10 minutes to generate and test new token


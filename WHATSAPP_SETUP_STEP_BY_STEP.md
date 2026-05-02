# WhatsApp API Setup - Step by Step Guide

## 📱 What You'll Get

- Send AI-generated messages to your sales reps via WhatsApp
- Receive replies from reps automatically
- Track message delivery and read status
- Professional business messaging

---

## 🚀 Step 1: Create Meta Business Account (5 minutes)

### 1.1 Go to Meta Business Suite
- Open: https://business.facebook.com/
- Click **"Create Account"** (if you don't have one)
- Fill in:
  - Business Name: **Hi-Tech International Group**
  - Your Name: **Your Name**
  - Business Email: **Your Email**

### 1.2 Verify Your Business
- Add business details
- Verify email address
- Complete business verification (may take 1-2 days for full verification)

**Note:** You can start testing immediately even without full verification!

---

## 🔧 Step 2: Create WhatsApp Business App (10 minutes)

### 2.1 Go to Meta for Developers
- Open: https://developers.facebook.com/
- Click **"My Apps"** → **"Create App"**

### 2.2 Choose App Type
- Select: **"Business"**
- Click **"Next"**

### 2.3 Fill App Details
- App Name: **Hi-Tech AI Sales**
- App Contact Email: **Your Email**
- Business Account: **Select your business** (created in Step 1)
- Click **"Create App"**

### 2.4 Add WhatsApp Product
- In your app dashboard, find **"Add Products"**
- Find **"WhatsApp"** and click **"Set Up"**

---

## 📞 Step 3: Get Test Phone Number (2 minutes)

### 3.1 Quick Start
- You'll see **"WhatsApp" → "Getting Started"**
- Meta provides a **TEST phone number** automatically
- You'll see something like:
  ```
  Test Phone Number: +1 555 025 3483
  Phone Number ID: 106540352242922
  ```

### 3.2 Copy Your Credentials
**Copy these two values:**

1. **Phone Number ID**: `106540352242922` (example)
   - Found under "Phone Number ID"
   
2. **Temporary Access Token**: `EAABsbCS1iHgBO7fZC...` (long string)
   - Found under "Temporary access token"
   - Click **"Copy"** button

**⚠️ Important:** 
- Temporary token expires in 24 hours
- For production, you'll generate a permanent token (Step 6)
- For now, use temporary token for testing

---

## 📝 Step 4: Add Test Recipients (3 minutes)

### 4.1 Add Your WhatsApp Number
- In the same page, scroll to **"To"** section
- Click **"Add phone number"**
- Enter your WhatsApp number (with country code)
  - Example: `+919876543210`
- Click **"Send Code"**
- Enter the code you receive on WhatsApp
- Click **"Verify"**

### 4.2 Add More Numbers (Optional)
- You can add up to 5 test numbers
- Add your team members' numbers
- Each needs to verify via WhatsApp code

---

## ⚙️ Step 5: Configure Your Application (5 minutes)

### 5.1 Open Your .env File
```bash
# On Windows
notepad .env

# Or use any text editor
```

### 5.2 Update WhatsApp Settings
Find the WhatsApp section and update:

```env
# ── WhatsApp Meta Cloud API ──────────────────
WHATSAPP_PHONE_NUMBER_ID=106540352242922    # Your Phone Number ID
WHATSAPP_ACCESS_TOKEN=EAABsbCS1iHgBO7fZC...  # Your Access Token (long string)
WHATSAPP_VERIFY_TOKEN=hitech-verify-2026     # Keep this as is
WHATSAPP_API_VERSION=v20.0                   # Keep this as is

# ── Mukul (owner config) ─────────────────────
MUKUL_PHONE=919876543210                     # Your WhatsApp number (no + sign)
MUKUL_NAME=Mukul Sareen
```

**Important:**
- Remove the `+` sign from phone numbers
- Just use country code + number: `919876543210`
- Access token is very long (200+ characters) - copy the entire thing

### 5.3 Save the File
- Save `.env` file
- Close the editor

---

## 🔄 Step 6: Restart Server (1 minute)

### 6.1 Stop Current Server
If server is running in terminal:
- Press `Ctrl+C` to stop

### 6.2 Start Server Again
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8002
INFO:     Application startup complete.
```

---

## ✅ Step 7: Test WhatsApp Integration (3 minutes)

### 7.1 Run Test Script
```bash
python test_whatsapp.py
```

**Expected Output:**
```
Testing WhatsApp Integration
============================================================

1. Checking Configuration:
   Phone Number ID: 106540352242922
   Access Token: ✅ Set
   API Version: v20.0

2. Testing Connection:
   ✅ WhatsApp API is accessible

============================================================
WhatsApp test complete!
```

### 7.2 Test in Settings Page
1. Open: http://localhost:8002/frontend/index.html
2. Click **"Settings"** tab
3. Scroll to **"WhatsApp Business API"** section
4. Should show: **"● Connected"**
5. Click **"Test connection"** button

### 7.3 Send Test Message
1. Go to **"Inbox"** tab
2. Click any conversation
3. Click **"◆ Generate AI Nudge"** button
4. AI will generate a message
5. Click **"Send"** button
6. Check your WhatsApp - you should receive the message!

---

## 🔐 Step 8: Generate Permanent Token (For Production)

**Note:** Temporary token expires in 24 hours. For production use, generate permanent token.

### 8.1 Create System User
1. Go to: https://business.facebook.com/settings/system-users
2. Click **"Add"**
3. Name: **Hi-Tech AI System**
4. Role: **Admin**
5. Click **"Create System User"**

### 8.2 Generate Token
1. Click on the system user you just created
2. Click **"Generate New Token"**
3. Select your app: **Hi-Tech AI Sales**
4. Select permissions:
   - ✅ `whatsapp_business_messaging`
   - ✅ `whatsapp_business_management`
5. Click **"Generate Token"**
6. **Copy the token** (you won't see it again!)

### 8.3 Update .env with Permanent Token
```env
WHATSAPP_ACCESS_TOKEN=your_permanent_token_here
```

### 8.4 Restart Server
```bash
# Stop server (Ctrl+C)
# Start again
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

---

## 🌐 Step 9: Setup Webhook (For Receiving Messages)

**Note:** This requires your server to be accessible from the internet.

### 9.1 For Local Testing - Use ngrok
```bash
# Install ngrok: https://ngrok.com/download
# Run ngrok
ngrok http 8002
```

You'll get a URL like: `https://abc123.ngrok.io`

### 9.2 Configure Webhook in Meta
1. Go to your app dashboard
2. Click **"WhatsApp" → "Configuration"**
3. Find **"Webhook"** section
4. Click **"Edit"**

**Enter:**
- Callback URL: `https://abc123.ngrok.io/api/whatsapp/webhook`
- Verify Token: `hitech-verify-2026`

5. Click **"Verify and Save"**

### 9.3 Subscribe to Events
Check these boxes:
- ✅ `messages` - Receive incoming messages
- ✅ `message_status` - Track delivery status

6. Click **"Save"**

---

## 📊 Step 10: Verify Everything Works

### 10.1 Check Settings Page
- Open: http://localhost:8002/frontend/index.html
- Go to Settings
- WhatsApp section should show: **"● Connected"**

### 10.2 Send Test Message
1. Go to Inbox
2. Select a conversation
3. Generate AI message
4. Send it
5. Check your WhatsApp

### 10.3 Reply to Message (If webhook setup)
1. Reply to the message on WhatsApp
2. Check your app - reply should appear in conversation

---

## 🎯 Quick Reference

### Your Credentials:
```
Phone Number ID: ________________
Access Token: ________________
Verify Token: hitech-verify-2026
```

### Important URLs:
- Meta Business: https://business.facebook.com/
- Developers: https://developers.facebook.com/
- System Users: https://business.facebook.com/settings/system-users
- Your App: http://localhost:8002/frontend/index.html

### Test Commands:
```bash
# Test WhatsApp
python test_whatsapp.py

# Restart server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

---

## 🆘 Troubleshooting

### "Phone Number ID not set"
- Check `.env` file has `WHATSAPP_PHONE_NUMBER_ID=...`
- Make sure no spaces around `=`
- Restart server after updating

### "Access Token invalid"
- Token might have expired (temporary tokens last 24 hours)
- Generate new token from Meta dashboard
- Update `.env` and restart server

### "Message not delivered"
- Check recipient number is verified in Meta dashboard
- For testing, only verified numbers can receive messages
- Check phone number format: `919876543210` (no + or spaces)

### "Webhook verification failed"
- Check verify token matches: `hitech-verify-2026`
- Make sure server is accessible from internet (use ngrok for local)
- Check webhook URL is correct

---

## ✅ Checklist

Before you start:
- [ ] Meta Business Account created
- [ ] Meta Developer Account created
- [ ] WhatsApp Business App created
- [ ] Test phone number obtained
- [ ] Your WhatsApp number verified
- [ ] Phone Number ID copied
- [ ] Access Token copied
- [ ] `.env` file updated
- [ ] Server restarted
- [ ] Test script run successfully
- [ ] Settings page shows "Connected"
- [ ] Test message sent successfully

---

## 🚀 You're Ready!

Once all steps are complete:
- ✅ WhatsApp integration is live
- ✅ AI can send messages to reps
- ✅ Messages appear in WhatsApp
- ✅ Delivery status tracked
- ✅ (Optional) Receive replies via webhook

**Total Setup Time: ~30 minutes**

**Need help? Check the troubleshooting section or Meta's documentation:**
- https://developers.facebook.com/docs/whatsapp/cloud-api/get-started

---

**Let's get started! Follow Step 1 above.** 🚀

# WhatsApp & Email Integration Guide

## ✅ Language Set to English Only

All 96 reps are now set to `english_only` language. All AI-generated messages will be in pure professional English with no Hindi words.

---

## 📱 WhatsApp Business API Integration

### What You Need:

1. **Meta Business Account** (Facebook Business Manager)
2. **WhatsApp Business API Access**
3. **Phone Number ID** - From Meta Business
4. **Access Token** - From Meta Business
5. **Webhook URL** - Your server URL for receiving messages

### Step-by-Step Setup:

#### 1. Get WhatsApp Business API Access

1. Go to https://business.facebook.com/
2. Create a Business Account (if you don't have one)
3. Go to https://developers.facebook.com/
4. Create an App → Select "Business" type
5. Add "WhatsApp" product to your app

#### 2. Get Your Credentials

**Phone Number ID:**
- In your Meta App Dashboard
- Go to WhatsApp → API Setup
- Copy the "Phone number ID" (looks like: `106540352242922`)

**Access Token:**
- In the same page, copy the "Temporary access token"
- For production, generate a permanent token:
  - Go to System Users in Business Settings
  - Create a system user
  - Generate a permanent token with `whatsapp_business_messaging` permission

#### 3. Configure Webhook

**Webhook URL:** `https://your-domain.com/api/whatsapp/webhook`

**Setup:**
1. In Meta App Dashboard → WhatsApp → Configuration
2. Click "Edit" on Webhook
3. Enter your webhook URL
4. Enter Verify Token: `hitech-verify-2026` (or any secret string)
5. Subscribe to these fields:
   - `messages` (incoming messages)
   - `message_status` (delivery status)

#### 4. Update Your .env File

```env
# WhatsApp Business API
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_VERIFY_TOKEN=hitech-verify-2026
WHATSAPP_API_VERSION=v20.0
```

#### 5. Test WhatsApp Integration

```bash
# Test sending a message
curl -X POST http://localhost:8002/api/whatsapp/send-test \
  -H "Content-Type: application/json" \
  -d '{"to": "919876543210", "message": "Test from Hi-Tech AI"}'
```

### WhatsApp Features Available:

✅ **Send Messages** - AI-generated nudges to reps
✅ **Receive Messages** - Rep replies via webhook
✅ **Message Status** - Track delivery/read status
✅ **Templates** - Pre-approved message templates
✅ **Media** - Send images, documents, PDFs

### Current Implementation:

The app already has WhatsApp integration code in:
- `app/api/whatsapp.py` - Webhook endpoints
- `app/services/whatsapp_api.py` - Send message functions

Just add your credentials to `.env` and it will work!

---

## 📧 Email / Gmail Integration

### Option 1: Gmail API (Recommended)

#### What You Need:

1. **Google Cloud Project**
2. **Gmail API Enabled**
3. **OAuth 2.0 Credentials**
4. **Client ID & Secret**

#### Step-by-Step Setup:

1. **Create Google Cloud Project:**
   - Go to https://console.cloud.google.com/
   - Create a new project: "Hi-Tech AI Sales"

2. **Enable Gmail API:**
   - In your project, go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

3. **Create OAuth Credentials:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Web application"
   - Authorized redirect URIs: `http://localhost:8002/api/gmail/callback`
   - Copy the Client ID and Client Secret

4. **Update .env:**

```env
# Gmail API
GMAIL_CLIENT_ID=your_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REDIRECT_URI=http://localhost:8002/api/gmail/callback
```

5. **Authorize Gmail:**
   - Go to http://localhost:8002/api/gmail/authorize
   - Sign in with your Gmail account
   - Grant permissions
   - You'll be redirected back with authorization

### Option 2: SMTP (Simpler, but less features)

#### What You Need:

1. **Gmail Account**
2. **App Password** (if using Gmail)

#### Setup for Gmail SMTP:

1. **Enable 2-Factor Authentication** on your Gmail account

2. **Generate App Password:**
   - Go to https://myaccount.google.com/security
   - Under "2-Step Verification", click "App passwords"
   - Select "Mail" and "Other (Custom name)"
   - Name it "Hi-Tech AI Sales"
   - Copy the 16-character password

3. **Update .env:**

```env
# Email SMTP
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your_app_password_here
EMAIL_FROM_NAME=Hi-Tech AI Sales
EMAIL_FROM_ADDRESS=your-email@gmail.com
```

#### Setup for Other Email Providers:

**Outlook/Office 365:**
```env
EMAIL_SMTP_HOST=smtp.office365.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your-email@outlook.com
EMAIL_SMTP_PASSWORD=your_password
```

**Custom Domain (e.g., @hitechgroup.in):**
```env
EMAIL_SMTP_HOST=mail.hitechgroup.in
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=ai@hitechgroup.in
EMAIL_SMTP_PASSWORD=your_password
```

### Email Features Available:

✅ **Send Emails** - Formal communications to customers
✅ **HTML Templates** - Professional email designs
✅ **Attachments** - Send PDFs, quotes, documents
✅ **CC/BCC** - Copy Mukul or seniors
✅ **Read Receipts** - Track email opens (with Gmail API)

---

## 🔧 Quick Setup Commands

### 1. Update .env with your credentials:

```bash
# Edit .env file
nano .env

# Or use Windows notepad
notepad .env
```

### 2. Restart the server to load new config:

```bash
# Stop current server (Ctrl+C in terminal)
# Or use the process manager
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### 3. Test integrations:

```bash
# Test WhatsApp
python test_whatsapp.py

# Test Email
python test_email.py
```

---

## 📝 Configuration Summary

### Current Status:

✅ **Language**: All reps set to `english_only`
✅ **NVIDIA AI**: Configured and working
✅ **CRM**: Connected and syncing
✅ **Database**: 9,309 conversations ready

### Need to Configure:

⚠️ **WhatsApp**: Add credentials to `.env`
⚠️ **Email**: Choose Gmail API or SMTP and configure

### After Configuration:

1. Update `.env` with your credentials
2. Restart server
3. Go to Settings page
4. Test connections
5. Start sending messages!

---

## 🎯 Next Steps

1. **Choose your email method**: Gmail API (more features) or SMTP (simpler)
2. **Get WhatsApp credentials** from Meta Business
3. **Update .env file** with all credentials
4. **Restart server**
5. **Test in Settings page**

Need help with any specific step? Let me know!

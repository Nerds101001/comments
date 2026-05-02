# Integration Setup Complete Guide

## ✅ What's Done

### 1. Language Set to English Only
- All 96 reps updated to `english_only` language
- All AI responses will be in pure professional English
- No Hindi words will be used

### 2. Email Service Created
- SMTP email service implemented
- Professional HTML email templates
- Support for attachments, CC, BCC
- Test script created

### 3. Configuration Files Updated
- `.env` updated with email settings
- `app/config.py` updated with email config
- Email service module created

---

## 📋 What You Need to Provide

### For WhatsApp Integration:

1. **Phone Number ID** - From Meta Business
2. **Access Token** - From Meta Business

### For Email Integration:

Choose ONE option:

**Option A: Gmail (Recommended)**
1. Your Gmail address
2. App Password (generated from Google Account)

**Option B: Other Email Provider**
1. SMTP host (e.g., smtp.office365.com)
2. SMTP port (usually 587)
3. Email address
4. Email password

---

## 🚀 Step-by-Step Setup

### Step 1: Get WhatsApp Credentials

1. Go to https://business.facebook.com/
2. Create/Login to Business Account
3. Go to https://developers.facebook.com/
4. Create App → Business type
5. Add WhatsApp product
6. Go to WhatsApp → API Setup
7. Copy:
   - **Phone Number ID** (e.g., `106540352242922`)
   - **Access Token** (starts with `EAAB...`)

### Step 2: Get Email Credentials

**For Gmail:**

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already)
3. Go to https://myaccount.google.com/apppasswords
4. Create App Password:
   - Select "Mail"
   - Select "Other (Custom name)"
   - Name it "Hi-Tech AI Sales"
5. Copy the 16-character password

**For Other Providers:**

Just have your email login credentials ready.

### Step 3: Update .env File

Open `.env` file and fill in your credentials:

```env
# ── WhatsApp Meta Cloud API ──────────────────
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_VERIFY_TOKEN=hitech-verify-2026
WHATSAPP_API_VERSION=v20.0

# ── Email SMTP (for sending emails) ──────────
# For Gmail:
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your_16_char_app_password
EMAIL_FROM_NAME=Hi-Tech AI Sales
EMAIL_FROM_ADDRESS=your-email@gmail.com

# ── Mukul (owner config) ─────────────────────
MUKUL_PHONE=919876543210            # Your WhatsApp number (with country code, no +)
MUKUL_NAME=Mukul Sareen
```

### Step 4: Restart Server

Stop and restart the server to load new configuration:

```bash
# If server is running in terminal, press Ctrl+C
# Then restart:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

Or use the process manager to restart.

### Step 5: Test Integrations

```bash
# Test WhatsApp
python test_whatsapp.py

# Test Email
python test_email.py
```

### Step 6: Verify in Settings Page

1. Open http://localhost:8002/frontend/index.html
2. Go to Settings tab
3. Scroll to WhatsApp section - should show "● Connected"
4. Scroll to Email section - should show "● Connected"
5. Click "Test connection" buttons to verify

---

## 📱 WhatsApp Setup Details

### What You'll Get:

- **Send Messages**: AI-generated nudges to reps via WhatsApp
- **Receive Messages**: Rep replies come back via webhook
- **Message Status**: Track delivery and read status
- **Templates**: Use pre-approved message templates

### Webhook Setup (After Basic Setup):

1. In Meta App Dashboard → WhatsApp → Configuration
2. Click "Edit" on Webhook
3. Enter: `https://your-domain.com/api/whatsapp/webhook`
4. Verify Token: `hitech-verify-2026`
5. Subscribe to: `messages`, `message_status`

**Note**: For local testing, you'll need ngrok or similar to expose localhost.

---

## 📧 Email Setup Details

### What You'll Get:

- **Send Emails**: Professional emails to customers
- **HTML Templates**: Beautiful, branded emails
- **Attachments**: Send quotes, PDFs, documents
- **CC/BCC**: Copy Mukul or seniors on emails

### Email Templates Available:

1. **Customer Follow-up** - Professional follow-up emails
2. **Quote/Proposal** - Send quotes with attachments
3. **Meeting Confirmation** - Confirm meetings
4. **Thank You** - Post-purchase thank you

---

## 🧪 Testing

### Test WhatsApp:

```bash
python test_whatsapp.py
```

Expected output:
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

### Test Email:

```bash
python test_email.py
```

Expected output:
```
Testing Email/SMTP Integration
============================================================

1. Checking Configuration:
   SMTP Host: smtp.gmail.com
   SMTP Port: 587
   SMTP User: your-email@gmail.com
   SMTP Password: ✅ Set

2. Testing SMTP Connection:
   ✅ SMTP connection successful!

============================================================
Email test complete!
```

---

## 🎯 What Happens After Setup

### Automatic Features:

1. **AI Nudges via WhatsApp**:
   - AI generates message in English
   - Sends to rep's WhatsApp
   - Tracks delivery status

2. **Rep Replies**:
   - Rep replies on WhatsApp
   - Webhook receives message
   - AI analyzes and responds

3. **Email Communications**:
   - Send formal emails to customers
   - Professional HTML templates
   - Track sent emails

### Manual Features:

1. **Send Test Message**:
   - Go to any conversation
   - Click "Generate AI Nudge"
   - Click "Send via WhatsApp"

2. **Send Email**:
   - Go to any conversation
   - Click "Send Email"
   - Choose template
   - Send to customer

---

## 📝 Configuration Checklist

Before you start, make sure you have:

### WhatsApp:
- [ ] Meta Business Account created
- [ ] WhatsApp Business API access
- [ ] Phone Number ID copied
- [ ] Access Token copied
- [ ] Added to `.env` file

### Email:
- [ ] Email account ready (Gmail recommended)
- [ ] App Password generated (for Gmail)
- [ ] SMTP credentials ready
- [ ] Added to `.env` file

### General:
- [ ] `.env` file updated
- [ ] Server restarted
- [ ] Tests run successfully
- [ ] Settings page shows "Connected"

---

## 🆘 Troubleshooting

### WhatsApp Issues:

**"Not connected" in Settings:**
- Check Phone Number ID is correct
- Check Access Token is valid
- Restart server after updating .env

**"Failed to send message":**
- Verify phone number format (919876543210)
- Check WhatsApp Business API is active
- Verify token hasn't expired

### Email Issues:

**"SMTP connection failed":**
- For Gmail: Make sure 2FA is enabled
- For Gmail: Use App Password, not regular password
- Check SMTP host and port are correct
- Verify credentials are correct

**"Authentication failed":**
- Gmail: Generate new App Password
- Other: Check username/password
- Check if account allows SMTP access

---

## 📚 Additional Resources

### WhatsApp:
- Meta Business: https://business.facebook.com/
- WhatsApp API Docs: https://developers.facebook.com/docs/whatsapp
- Get Started: https://developers.facebook.com/docs/whatsapp/cloud-api/get-started

### Email:
- Gmail App Passwords: https://myaccount.google.com/apppasswords
- Gmail SMTP Settings: https://support.google.com/mail/answer/7126229
- Outlook SMTP: https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings

---

## ✅ Summary

**Completed:**
- ✅ All reps set to English only
- ✅ Email service created
- ✅ Configuration files updated
- ✅ Test scripts created
- ✅ Documentation complete

**Next Steps:**
1. Get WhatsApp credentials from Meta Business
2. Get Email credentials (Gmail App Password)
3. Update `.env` file
4. Restart server
5. Run test scripts
6. Start using integrations!

**Need help?** Check the troubleshooting section or refer to the detailed guides:
- `WHATSAPP_EMAIL_INTEGRATION_GUIDE.md` - Detailed setup guide
- `test_whatsapp.py` - WhatsApp test script
- `test_email.py` - Email test script

---

**You're all set! Just add your credentials and you're ready to go!** 🚀

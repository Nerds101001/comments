# Quick Integration Guide

## ✅ Done

1. **All AI responses now in English only** (no Hindi)
2. **Email service created** and ready to use
3. **Configuration files updated**
4. **Test scripts created**

---

## 🎯 What You Need to Do

### 1. Get WhatsApp Credentials (5 minutes)

1. Go to https://business.facebook.com/
2. Go to https://developers.facebook.com/
3. Create App → Add WhatsApp
4. Copy **Phone Number ID** and **Access Token**

### 2. Get Email Credentials (3 minutes)

**For Gmail (Recommended):**
1. Go to https://myaccount.google.com/apppasswords
2. Create App Password for "Mail"
3. Copy the 16-character password

### 3. Update .env File (2 minutes)

Open `.env` and add:

```env
# WhatsApp
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_access_token

# Email (Gmail example)
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your_app_password
EMAIL_FROM_ADDRESS=your-email@gmail.com

# Your WhatsApp number
MUKUL_PHONE=919876543210
```

### 4. Restart Server (1 minute)

```bash
# Stop server (Ctrl+C)
# Restart:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### 5. Test (2 minutes)

```bash
python test_whatsapp.py
python test_email.py
```

---

## 📋 Credentials Checklist

### WhatsApp:
- [ ] Phone Number ID: `________________`
- [ ] Access Token: `EAAB________________`

### Email:
- [ ] Email: `________________@gmail.com`
- [ ] App Password: `________________`

### Your Info:
- [ ] WhatsApp Number: `919________________`

---

## 🚀 After Setup

### What Works:

✅ **AI Messages in English** - All responses in professional English
✅ **WhatsApp Integration** - Send/receive messages
✅ **Email Integration** - Send professional emails
✅ **CRM Sync** - Auto-sync every 60 minutes
✅ **Dashboard** - View all conversations
✅ **Inbox** - Manage conversations

### How to Use:

1. **Send WhatsApp Message**:
   - Open conversation
   - Click "Generate AI Nudge"
   - Message sent via WhatsApp

2. **Send Email**:
   - Open conversation
   - Click "Send Email"
   - Professional email sent

3. **View Sync Status**:
   - Go to Settings
   - See "CRM Sync Status"
   - Click "⟳ Sync Now" to sync manually

---

## 📚 Documentation

- `INTEGRATION_SETUP_COMPLETE.md` - Full setup guide
- `WHATSAPP_EMAIL_INTEGRATION_GUIDE.md` - Detailed instructions
- `test_whatsapp.py` - Test WhatsApp
- `test_email.py` - Test Email

---

## 🆘 Quick Troubleshooting

**WhatsApp not working?**
- Check credentials in `.env`
- Restart server
- Run `python test_whatsapp.py`

**Email not working?**
- Gmail: Use App Password, not regular password
- Enable 2FA first
- Run `python test_email.py`

**Still issues?**
- Check `.env` file has no typos
- Make sure server restarted
- Check Settings page shows "Connected"

---

**Total Setup Time: ~15 minutes** ⏱️

**Ready to integrate? Let's go!** 🚀

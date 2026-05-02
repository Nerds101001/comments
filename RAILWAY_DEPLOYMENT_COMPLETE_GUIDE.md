# 🚀 Complete Railway Deployment Guide

## ⚠️ IMPORTANT: Fix Path Length Issue First!

Your current folder path is too long for Git on Windows. Follow these steps:

---

## 📁 Step 1: Move to Shorter Path (2 minutes)

### Option A: Copy to Desktop
1. **Copy this entire folder**
2. **Paste to Desktop**
3. **Rename to**: `hitech-ai`
4. **New path**: `C:\Users\the_Nerds\Desktop\hitech-ai`

### Option B: Copy to C Drive
1. **Copy this entire folder**
2. **Paste to**: `C:\`
3. **Rename to**: `hitech-ai`
4. **New path**: `C:\hitech-ai`

---

## 🔧 Step 2: Push to GitHub (5 minutes)

### Method 1: Using Command Line (Recommended)

Open **Command Prompt** or **PowerShell** in the new location:

```bash
# Navigate to folder
cd C:\Users\the_Nerds\Desktop\hitech-ai

# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Initial commit - Hi-Tech AI Sales System"

# Connect to GitHub
git remote add origin https://github.com/Nerds101001/comments.git

# Push
git branch -M main
git push -u origin main --force
```

### Method 2: Using GitHub Desktop (Easier)

1. Download: https://desktop.github.com
2. Install and sign in
3. **File** → **Add Local Repository**
4. Select: `C:\Users\the_Nerds\Desktop\hitech-ai`
5. Click **Publish repository**
6. Repository name: `comments`
7. Account: `Nerds101001`
8. Click **Publish**

---

## 🚂 Step 3: Deploy to Railway (5 minutes)

### 3.1 Create Railway Account

1. Go to: https://railway.app
2. Click **Login**
3. Sign in with **GitHub**
4. Authorize Railway

### 3.2 Create New Project

1. Click **New Project**
2. Select **Deploy from GitHub repo**
3. Choose: `Nerds101001/comments`
4. Railway will start building automatically

### 3.3 Add Environment Variables

Click on your project → **Variables** tab → Add these:

```env
AI_API_KEY=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
AI_MODEL=openai/gpt-oss-120b
AI_BASE_URL=https://integrate.api.nvidia.com/v1
AI_PROVIDER=nvidia

WHATSAPP_PHONE_NUMBER_ID=1105349452662677
WHATSAPP_ACCESS_TOKEN=EAA9EqzplgB4BReqyHSS8QReZBsxEmZBoSSfIukIAS5jbjyCd2ZCMvVjLzPpExXA5O4c603H8CgwKz5EV4VOIKvyD36vdRaKiRYSezVZC9yKFCwKpY25huQrRZAYbkcd4fLyabLZBs4Q4stzQuAw1ZCcxRkuTpZAhpD3MVvsBnPaWXBpB9cOC8W8KGLbZCnDTzwT52RY23c5c9KKyUcguBfDZBrpe5C2PRcaZChL6VVWFkGqKr1nRGjw3QiefpAp030csfn0jwPv48zKiuZBDR9k5ELI1AoKU
WHATSAPP_VERIFY_TOKEN=hitech-verify-2026
WHATSAPP_API_VERSION=v20.0

CRM_BASE_URL=https://api-crm.rustx.net
CRM_USERNAME=Nagender
CRM_PASSWORD=nag@8745
CRM_POLL_INTERVAL_MINUTES=60

MUKUL_PHONE=918264409000
MUKUL_NAME=Mukul Sareen

DATABASE_URL=sqlite+aiosqlite:///./hitech_sales.db

APP_SECRET_KEY=hitech-ai-sales-secret-key-2026
DEBUG=false
```

### 3.4 Deploy!

1. Railway will automatically deploy
2. Wait 2-3 minutes for build to complete
3. Click **View Logs** to monitor progress

### 3.5 Get Your URL

1. Go to **Settings** tab
2. Click **Generate Domain**
3. Your app will be at: `https://your-app.railway.app`

---

## ✅ Step 4: Verify Deployment (2 minutes)

### Check These URLs:

1. **Frontend**: `https://your-app.railway.app/frontend/index.html`
2. **API Docs**: `https://your-app.railway.app/docs`
3. **Health Check**: `https://your-app.railway.app/api/dashboard/summary`

### Expected Results:

- ✅ Frontend loads with Dashboard, Inbox, Command Centre tabs
- ✅ API docs show all endpoints
- ✅ Dashboard shows 96 reps, 9,309 conversations

---

## 🔧 Step 5: Configure WhatsApp Webhook (Optional)

If you want to receive WhatsApp replies:

1. Go to Meta Developer Console
2. WhatsApp → Configuration → Webhook
3. **Callback URL**: `https://your-app.railway.app/api/whatsapp/webhook`
4. **Verify Token**: `hitech-verify-2026`
5. Click **Verify and Save**
6. Subscribe to: `messages` and `message_status`

---

## 💰 Billing

### Railway Pricing:
- **Starter**: $5/month
- **Includes**: 
  - 512MB RAM
  - Persistent storage
  - Automatic HTTPS
  - Custom domains
  - Unlimited bandwidth

### Payment Setup:
1. Go to **Account Settings**
2. Click **Billing**
3. Add payment method
4. Select **Starter Plan**

---

## 📊 Monitoring

### View Logs:
1. Click on your project
2. Go to **Deployments** tab
3. Click on latest deployment
4. View real-time logs

### Check Status:
- Green = Running ✅
- Yellow = Building 🔨
- Red = Error ❌

---

## 🆘 Troubleshooting

### Build Failed?
- Check logs for errors
- Verify `requirements.txt` is present
- Ensure Python version is correct

### App Not Starting?
- Check environment variables are set
- View logs for startup errors
- Verify PORT is not hardcoded

### Database Issues?
- Railway provides persistent volumes
- Database is automatically created
- Check logs for SQLite errors

### CRM Sync Not Working?
- Verify CRM credentials
- Check logs for API errors
- Test CRM connection manually

---

## 🎯 What You'll Have

After deployment:

- ✅ **Live URL**: Accessible from anywhere
- ✅ **HTTPS**: Automatic SSL certificate
- ✅ **24/7 Uptime**: Always running
- ✅ **Auto-restart**: If app crashes
- ✅ **CRM Sync**: Every 60 minutes
- ✅ **WhatsApp**: Ready to send messages
- ✅ **AI Nudges**: Working perfectly
- ✅ **Database**: Persistent storage
- ✅ **Logs**: Real-time monitoring

---

## 📝 Quick Checklist

Before deploying:
- [ ] Copied folder to shorter path
- [ ] Pushed to GitHub
- [ ] Created Railway account
- [ ] Connected GitHub to Railway
- [ ] Added all environment variables
- [ ] Deployed successfully
- [ ] Verified frontend loads
- [ ] Checked API docs
- [ ] Tested a few endpoints
- [ ] Added payment method

---

## 🔗 Important Links

- **Railway Dashboard**: https://railway.app/dashboard
- **GitHub Repo**: https://github.com/Nerds101001/comments
- **Railway Docs**: https://docs.railway.app
- **Your App**: `https://your-app.railway.app`

---

## 🎉 Success!

Once deployed, share your app URL with your team:

**Frontend**: `https://your-app.railway.app/frontend/index.html`

Everyone can access:
- Dashboard
- Inbox (9,309 conversations)
- Command Centre
- Settings

---

**Total Time**: ~15 minutes
**Cost**: $5/month
**Difficulty**: ⭐ Easy

**Need help?** Check the logs or Railway documentation!

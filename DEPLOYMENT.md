# Hi-Tech AI Sales - Railway Deployment Guide

## 🚀 Quick Deploy to Railway

### Prerequisites
- GitHub account
- Railway account (sign up at https://railway.app)

### Step 1: Push to GitHub

This code is already pushed to: https://github.com/Nerds101001/comments

### Step 2: Deploy to Railway

1. **Go to Railway**: https://railway.app
2. **Sign in** with GitHub
3. **Click**: "New Project"
4. **Select**: "Deploy from GitHub repo"
5. **Choose**: `Nerds101001/comments`
6. **Railway will auto-detect** Python and start building

### Step 3: Add Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```
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
```

### Step 4: Deploy!

Railway will automatically:
- ✅ Install dependencies
- ✅ Create database
- ✅ Start the server
- ✅ Assign a public URL

### Step 5: Access Your App

Your app will be available at:
- **Frontend**: `https://your-app.railway.app/frontend/index.html`
- **API Docs**: `https://your-app.railway.app/docs`

## 🔧 Configuration

### Custom Domain (Optional)
1. Go to **Settings** → **Domains**
2. Click **Generate Domain** or add your own

### Database Persistence
Railway automatically provides persistent storage for SQLite.

### Logs
View logs in Railway dashboard under **Deployments** tab.

## 💰 Cost

- **Starter Plan**: $5/month
- Includes: 512MB RAM, persistent storage, automatic HTTPS

## 🆘 Troubleshooting

### App not starting?
- Check logs in Railway dashboard
- Verify all environment variables are set
- Ensure PORT is not hardcoded (Railway sets it automatically)

### Database issues?
- Railway provides persistent volumes automatically
- Database file is stored in `/app/hitech_sales.db`

### CRM sync not working?
- Check CRM credentials in environment variables
- View logs for sync errors

## 📝 Notes

- Railway automatically restarts your app if it crashes
- Logs are available for 7 days
- Database is backed up automatically
- HTTPS is enabled by default

## 🎯 What Works

- ✅ FastAPI server runs 24/7
- ✅ CRM auto-sync every 60 minutes
- ✅ WhatsApp integration
- ✅ AI nudge generation
- ✅ SQLite database with persistence
- ✅ Background scheduler
- ✅ All 96 reps with phone numbers
- ✅ 9,309 conversations

## 🔗 Links

- Railway Dashboard: https://railway.app/dashboard
- GitHub Repo: https://github.com/Nerds101001/comments
- Railway Docs: https://docs.railway.app

---

**Deployment Time**: ~10 minutes
**Cost**: $5/month
**Difficulty**: ⭐ Easy

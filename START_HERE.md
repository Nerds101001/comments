# 🚀 START HERE - Deploy to Railway

## ⚡ Quick Start (15 minutes total)

Your Hi-Tech AI Sales system is ready to deploy! Follow these 3 simple steps:

---

## 📁 STEP 1: Fix Path Issue (2 minutes)

**Problem**: Current folder path is too long for Git on Windows.

**Solution**: Copy this folder to a shorter path.

### Do This Now:

1. **Copy this entire folder**
2. **Paste to Desktop**
3. **Rename to**: `hitech-ai`

**New path should be**: `C:\Users\the_Nerds\Desktop\hitech-ai`

---

## 🔧 STEP 2: Push to GitHub (5 minutes)

Open **Command Prompt** or **PowerShell** in the new folder:

```bash
cd C:\Users\the_Nerds\Desktop\hitech-ai

git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/Nerds101001/comments.git
git branch -M main
git push -u origin main --force
```

**OR** use **GitHub Desktop** (easier):
1. Download: https://desktop.github.com
2. Add local repository
3. Publish to `Nerds101001/comments`

---

## 🚂 STEP 3: Deploy to Railway (8 minutes)

### 3.1 Sign Up (1 minute)
- Go to: https://railway.app
- Sign in with GitHub

### 3.2 Create Project (2 minutes)
- Click **New Project**
- Select **Deploy from GitHub repo**
- Choose: `Nerds101001/comments`

### 3.3 Add Environment Variables (5 minutes)

Click **Variables** tab and paste this:

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
APP_SECRET_KEY=hitech-ai-sales-2026
DEBUG=false
```

### 3.4 Deploy!
- Railway will build automatically
- Wait 2-3 minutes
- Click **Generate Domain** in Settings

---

## ✅ Done!

Your app will be live at: `https://your-app.railway.app`

**Access:**
- Frontend: `https://your-app.railway.app/frontend/index.html`
- API Docs: `https://your-app.railway.app/docs`

---

## 💰 Cost

**$5/month** - Includes everything:
- 512MB RAM
- Persistent storage
- Automatic HTTPS
- 24/7 uptime
- Auto-restart

---

## 📚 Need More Help?

Read these files:
1. **RAILWAY_DEPLOYMENT_COMPLETE_GUIDE.md** - Detailed step-by-step
2. **DEPLOYMENT.md** - Technical details
3. **PUSH_TO_GITHUB.md** - Git troubleshooting

---

## 🆘 Quick Troubleshooting

**Git error "path too long"?**
→ Copy folder to Desktop first!

**Railway build failed?**
→ Check logs in Railway dashboard

**App not starting?**
→ Verify all environment variables are set

---

**Ready? Start with STEP 1 above!** 🚀

**Time**: 15 minutes
**Difficulty**: ⭐ Easy
**Cost**: $5/month

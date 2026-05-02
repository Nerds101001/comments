# 🔧 How to Add Environment Variables to Railway

## 📋 Two Methods Available

### Method 1: Copy-Paste Individual Variables (Recommended)

1. **Open Railway Dashboard**
   - Go to your project
   - Click **Variables** tab

2. **Add Each Variable**
   - Click **+ New Variable**
   - Copy from `RAILWAY_ENV_VARIABLES.txt`
   - Paste one at a time

**Example:**
```
Variable Name: AI_API_KEY
Value: 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
```

---

### Method 2: Raw Editor (Faster)

1. **Open Railway Dashboard**
   - Go to your project
   - Click **Variables** tab

2. **Switch to Raw Editor**
   - Click **Raw Editor** button (top right)

3. **Copy All Variables**
   - Open `RAILWAY_ENV_RAW.txt`
   - Copy everything (Ctrl+A, Ctrl+C)
   - Paste into Railway Raw Editor
   - Click **Save**

---

## 📁 Files Available

### `RAILWAY_ENV_VARIABLES.txt`
- Format: `KEY="value"`
- Use for: Individual copy-paste
- Best for: Adding one by one

### `RAILWAY_ENV_RAW.txt`
- Format: `KEY=value`
- Use for: Raw Editor
- Best for: Bulk paste

---

## ✅ Complete List of Variables

**Total: 17 variables**

### AI Configuration (4 variables)
- `AI_API_KEY`
- `AI_BASE_URL`
- `AI_MODEL`
- `AI_PROVIDER`

### CRM Configuration (4 variables)
- `CRM_BASE_URL`
- `CRM_PASSWORD`
- `CRM_USERNAME`
- `CRM_POLL_INTERVAL_MINUTES`

### WhatsApp Configuration (4 variables)
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_API_VERSION`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_VERIFY_TOKEN`

### Application Configuration (5 variables)
- `DATABASE_URL`
- `MUKUL_NAME`
- `MUKUL_PHONE`
- `APP_SECRET_KEY`
- `DEBUG`

---

## 🎯 Step-by-Step Guide

### Step 1: Open Railway
Go to: https://railway.app/dashboard

### Step 2: Select Your Project
Click on: `comments` project

### Step 3: Open Variables Tab
Click: **Variables** (left sidebar)

### Step 4: Choose Method

**Option A: Raw Editor (Fastest)**
1. Click **Raw Editor** button
2. Open `RAILWAY_ENV_RAW.txt` from your project
3. Copy all content
4. Paste into Railway
5. Click **Save**

**Option B: Individual Variables**
1. Click **+ New Variable**
2. Copy variable name and value from `RAILWAY_ENV_VARIABLES.txt`
3. Paste and save
4. Repeat for all 17 variables

### Step 5: Deploy
Railway will automatically redeploy with new variables

---

## ⚠️ Important Notes

### Don't Include Quotes in Raw Editor
- ✅ Correct: `AI_API_KEY=nvapi-xxx`
- ❌ Wrong: `AI_API_KEY="nvapi-xxx"`

### Check for Spaces
- No spaces around `=` sign
- ✅ Correct: `KEY=value`
- ❌ Wrong: `KEY = value`

### Verify All Variables
After adding, verify count:
- Should have **17 variables** total
- Check each section is complete

---

## 🔍 Verification

After adding variables, check:
1. **Variables tab** shows 17 variables
2. **Deployment** starts automatically
3. **Logs** show "Application startup complete"
4. **App URL** is accessible

---

## 🆘 Troubleshooting

### Variables Not Saving?
- Check for syntax errors
- Remove extra spaces
- Don't use quotes in Raw Editor

### App Not Starting?
- Verify all 17 variables are present
- Check logs for missing variable errors
- Ensure no typos in variable names

### CRM Not Connecting?
- Verify `CRM_PASSWORD=nag@8745`
- Check `CRM_USERNAME=Nagender`
- Ensure `CRM_BASE_URL` is correct

---

## ✅ Quick Checklist

Before deploying:
- [ ] All 17 variables added
- [ ] No syntax errors
- [ ] No extra quotes in Raw Editor
- [ ] Deployment started automatically
- [ ] Logs show no errors
- [ ] App URL is accessible

---

## 🎉 Done!

Once all variables are added:
- Railway will automatically redeploy
- Wait 2-3 minutes for build
- Your app will be live!

**Access your app at**: `https://your-app.railway.app/frontend/index.html`

---

**Need help?** Check Railway logs for any errors!

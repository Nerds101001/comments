# 🌐 Use Railway Web Dashboard - Easiest Solution

## ❌ Why Railway CLI Doesn't Work

Railway CLI (`railway shell` and `railway run`) runs commands on **your local machine** with Railway environment variables. However:
- Your local machine can't access Railway's internal database
- The database hostname is only accessible from within Railway's network
- This causes the `socket.gaierror: [Errno 11001] getaddrinfo failed` error

---

## ✅ Solution: Use Railway Web Dashboard Shell

This runs commands **inside Railway's environment** where the database is accessible.

### Step-by-Step Instructions:

#### 1. Open Railway Dashboard
- Go to: **https://railway.app**
- Login to your account

#### 2. Navigate to Your Project
- Find and click on your project (the one with your FastAPI app)

#### 3. Select Your Service
- Click on your **FastAPI service** (NOT the Postgres service)
- You should see tabs like: Deployments, Metrics, Settings, etc.

#### 4. Open the Shell/Terminal
- Look for a **"Shell"**, **"Terminal"**, or **"Console"** tab
- Click on it to open the web-based terminal

#### 5. Run the Migration
In the web terminal, type:
```bash
python add_checkin_sync_tracking.py
```

Press Enter and wait for the output.

#### 6. Expected Output
```
✅ Added last_checkin_sync setting

📊 Current sync settings:
   last_checkin_sync: 2026-05-04T14:30:00.123456
   last_crm_sync: 2026-05-02T09:15:00.123456
```

---

## 🔄 Alternative: Auto-Run on Next Deployment

If you can't find the Shell tab, make the migration run automatically:

### Step 1: Check Railway Start Command
1. In Railway Dashboard → Your Service → **Settings**
2. Scroll to **"Deploy"** section
3. Find **"Start Command"** or **"Custom Start Command"**

### Step 2: Update Start Command
Change it to:
```bash
bash railway_startup.sh
```

### Step 3: Trigger Redeploy
1. Go to **"Deployments"** tab
2. Click **"Redeploy"** on the latest deployment
3. OR make a small change and push to git

### Step 4: Check Logs
1. Go to **"Deployments"** tab
2. Click on the latest deployment
3. Look for logs showing:
```
🚀 Running Railway startup tasks...
📊 Running check-in sync tracking migration...
✅ Added last_checkin_sync setting
🌐 Starting FastAPI application...
```

---

## 🎯 Recommended Approach

**Use the Web Dashboard Shell** because:
- ✅ Runs inside Railway's environment
- ✅ Has access to the database
- ✅ Immediate results
- ✅ No local connection issues

**Then set up auto-run** for future deployments:
- ✅ Update start command to `bash railway_startup.sh`
- ✅ Migration runs automatically on every deployment
- ✅ No manual intervention needed

---

## 📸 Visual Guide

### Finding the Shell Tab:
```
Railway Dashboard
└── Your Project
    └── Your FastAPI Service
        ├── Deployments
        ├── Metrics
        ├── Variables
        ├── Settings
        └── Shell ← Click here!
```

### What You'll See:
```
$ _  ← Blinking cursor in web terminal
```

### What to Type:
```bash
python add_checkin_sync_tracking.py
```

---

## ✅ Verify Migration Success

### Method 1: Check Your App
1. Open: `https://your-app.railway.app`
2. Go to **Settings** page
3. Verify:
   - ✅ Last Check-ins Sync appears
   - ✅ Total Check-ins count shows
   - ✅ CRM API shows "Connected"
   - ✅ AI Model shows actual model name

### Method 2: Check API
Open in browser or use curl:
```
https://your-app.railway.app/api/crm/sync-status
```

Look for `last_checkin_sync` in the JSON response.

### Method 3: Check Railway Logs
In Railway Dashboard:
1. Go to **Deployments** tab
2. Click on latest deployment
3. Look for migration success message

---

## 🐛 Troubleshooting

### Can't Find Shell Tab?
- Some Railway plans might not have shell access
- Use the **Auto-Run on Deployment** method instead

### Shell Tab is Disabled?
- Update start command to `bash railway_startup.sh`
- Redeploy to run migration automatically

### Migration Already Ran?
- That's OK! The script checks if the setting exists
- You'll see: `ℹ️  last_checkin_sync setting already exists`

---

## 🚀 Quick Summary

1. **Go to Railway Dashboard** (https://railway.app)
2. **Open your FastAPI service**
3. **Click "Shell" tab**
4. **Run:** `python add_checkin_sync_tracking.py`
5. **Verify** on Settings page

**OR**

1. **Update start command** to `bash railway_startup.sh`
2. **Redeploy**
3. **Check logs** for migration success
4. **Verify** on Settings page

---

**Use the Railway Web Dashboard Shell - it's the only way to run commands inside Railway's environment!** 🎉

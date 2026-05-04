# 🚀 Trigger Automatic Migration on Railway

## ✅ Easiest Solution: Let Railway Run It Automatically

Since we already have `railway_startup.sh` that runs the migration, we just need to make sure Railway uses it.

---

## 🔧 Method 1: Update Railway Start Command (Recommended)

### Step 1: Open Railway Dashboard
1. Go to https://railway.app
2. Login and open your project
3. Click on your **FastAPI service** (not Postgres)

### Step 2: Update Start Command
1. Click **"Settings"** tab
2. Scroll to **"Deploy"** section
3. Find **"Start Command"** or **"Custom Start Command"**
4. Change it to:
   ```bash
   bash railway_startup.sh
   ```
5. Click **"Save"** or **"Update"**

### Step 3: Trigger Redeploy
1. Go to **"Deployments"** tab
2. Click **"Redeploy"** on the latest deployment
3. OR push a small change to trigger auto-deploy

**The migration will run automatically before the app starts!**

---

## 🔧 Method 2: Use Railway Shell (Manual)

If you prefer to run it manually right now:

```bash
# Open Railway shell
railway shell

# Run the migration
python add_checkin_sync_tracking.py

# Exit
exit
```

---

## 🔧 Method 3: Use Railway Web Shell

1. Go to https://railway.app
2. Open your project
3. Click on your FastAPI service
4. Click **"Shell"** tab
5. Run: `python add_checkin_sync_tracking.py`

---

## 📋 What railway_startup.sh Does

```bash
#!/bin/bash
echo "🚀 Running Railway startup tasks..."

# Run migration (safe to run multiple times)
echo "📊 Running check-in sync tracking migration..."
python add_checkin_sync_tracking.py

# Start the application
echo "🌐 Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

This script:
1. ✅ Runs the migration first
2. ✅ Then starts your FastAPI app
3. ✅ Safe to run multiple times (checks if setting exists)
4. ✅ Runs on every deployment automatically

---

## ✅ Verify It's Working

### Check Railway Logs
```bash
railway logs --tail 100
```

Look for:
```
🚀 Running Railway startup tasks...
📊 Running check-in sync tracking migration...
✅ Added last_checkin_sync setting
🌐 Starting FastAPI application...
```

### Check Settings Page
1. Open: `https://your-app.railway.app`
2. Go to Settings page
3. Verify:
   - ✅ Last Check-ins Sync appears
   - ✅ Total Check-ins count shows
   - ✅ CRM API shows "Connected"
   - ✅ AI Model shows actual model name

---

## 🎯 Recommended Approach

**Use Method 1 (Update Start Command)** because:
- ✅ Migration runs automatically on every deployment
- ✅ No manual intervention needed
- ✅ Safe to run multiple times
- ✅ Ensures database is always up to date
- ✅ Works for future deployments too

---

## 🚀 Quick Steps

1. **Go to Railway Dashboard** → Your Service → Settings
2. **Update Start Command** to: `bash railway_startup.sh`
3. **Save and Redeploy**
4. **Check Logs** to verify migration ran
5. **Open Settings Page** to verify data shows correctly

---

**This is the easiest and most reliable method!** 🎉

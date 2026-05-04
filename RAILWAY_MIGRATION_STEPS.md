# 🚀 Railway Migration - Quick Steps

## ✅ Status: All Code Changes Already Pushed to Git

Latest commits:
- `0067bf5` - Minor updates to settings API and style learner
- `150651c` - Add auto-sync fix documentation
- `ff78c79` - Fix auto-sync scheduler: Add check-in sync and run initial sync on startup

---

## 🔧 Run Migration on Railway (3 Simple Commands)

Since you have Railway CLI installed, run these commands:

### Step 1: Login to Railway (if not already logged in)
```bash
railway login
```

### Step 2: Link to Your Project
```bash
railway link
```
- Select your project from the list
- Select the service (your FastAPI app)

### Step 3: Run the Migration
```bash
railway run python add_checkin_sync_tracking.py
```

**Expected Output:**
```
✅ Added last_checkin_sync setting

📊 Current sync settings:
   last_checkin_sync: 2026-05-04T...
   last_crm_sync: 2026-05-02T...
```

---

## 🔄 Alternative: If Railway CLI Has Connection Issues

### Option A: Use Railway Shell
```bash
railway shell
python add_checkin_sync_tracking.py
exit
```

### Option B: Use Railway Dashboard
1. Go to https://railway.app
2. Open your project
3. Click on your service
4. Click "Shell" or "Terminal" tab
5. Run: `python add_checkin_sync_tracking.py`

---

## ✅ Verify Migration Success

### Method 1: Check via API
```bash
curl https://your-app.railway.app/api/crm/sync-status
```

Look for `last_checkin_sync` in the response.

### Method 2: Check Settings Page
1. Open your app: `https://your-app.railway.app`
2. Go to Settings page
3. Look for "Last Check-ins Sync" timestamp

### Method 3: Check Railway Logs
```bash
railway logs --tail 50
```

Look for:
```
✅ Added last_checkin_sync setting
```

---

## 🎯 What This Migration Does

1. Adds `last_checkin_sync` setting to track check-in sync separately
2. Enables proper tracking of check-in sync vs comment sync
3. Fixes the Settings page to show real data from database
4. Enables auto-sync to run every 60 minutes for both comments and check-ins

---

## 🐛 Troubleshooting

### Issue: "railway: command not found"
```bash
# Install Railway CLI
npm install -g @railway/cli
```

### Issue: "No project linked"
```bash
railway link
```

### Issue: "Module not found"
```bash
railway run pip install -r requirements.txt
railway run python add_checkin_sync_tracking.py
```

---

## 📝 After Migration

Once migration is complete:
1. ✅ Settings page will show check-in sync data from database
2. ✅ Manual sync will sync both comments and check-ins
3. ✅ Auto-sync will run on startup and every 60 minutes
4. ✅ New counts will be displayed for both data types

---

**Ready?** Just run the 3 commands above! 🚀

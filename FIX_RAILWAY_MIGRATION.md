# 🔧 Fix Railway Migration - Use Railway Shell

## ❌ Problem

The `railway run` command is using your local environment variables instead of Railway's database credentials, causing a connection error.

## ✅ Solution: Use Railway Shell

Instead of `railway run`, use `railway shell` to run commands directly in the Railway environment.

---

## 🚀 Run Migration (Correct Method)

### Step 1: Open Railway Shell
```bash
railway shell
```

This will open a shell session connected to your Railway environment with all the correct environment variables.

### Step 2: Run the Migration
Once inside the Railway shell, run:
```bash
python add_checkin_sync_tracking.py
```

### Step 3: Exit the Shell
```bash
exit
```

---

## 📋 Complete Command Sequence

```bash
# Open Railway shell
railway shell

# Inside the shell, run:
python add_checkin_sync_tracking.py

# Exit when done
exit
```

**Expected Output:**
```
✅ Added last_checkin_sync setting

📊 Current sync settings:
   last_checkin_sync: 2026-05-04T...
   last_crm_sync: 2026-05-02T...
```

---

## 🔄 Alternative: Use Railway Dashboard

If the shell method doesn't work, use the web dashboard:

### Step 1: Open Railway Dashboard
1. Go to https://railway.app
2. Login to your account
3. Open your project

### Step 2: Find Your Service
1. Click on your FastAPI service (not the Postgres service)
2. Look for the **"Shell"** or **"Terminal"** tab
3. Click to open it

### Step 3: Run Migration
In the web shell, type:
```bash
python add_checkin_sync_tracking.py
```

Press Enter and wait for the output.

---

## 🎯 Why This Happens

- `railway run` executes commands locally but with Railway environment variables
- However, it still uses your local Python environment and network
- The database hostname from Railway can't be resolved from your local machine
- `railway shell` actually connects to the Railway container where everything is configured correctly

---

## ✅ After Migration

Once you see the success message, verify:

1. **Check Settings Page:**
   - Open: `https://your-app.railway.app`
   - Go to Settings page
   - Verify "Last Check-ins Sync" appears

2. **Check via API:**
   ```bash
   curl https://your-app.railway.app/api/crm/sync-status
   ```

3. **Check Railway Logs:**
   ```bash
   railway logs --tail 50
   ```

---

## 🚀 Quick Commands

```bash
# Method 1: Railway Shell (Recommended)
railway shell
python add_checkin_sync_tracking.py
exit

# Method 2: Check logs
railway logs --tail 50

# Method 3: Restart service (if needed)
railway restart
```

---

**Try the Railway shell method now!** 🎉

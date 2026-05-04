# Railway Migration Guide - Check-in Sync Tracking

## ✅ Changes Pushed to Git

All changes have been successfully pushed to the `main` branch:
- Commit: `641aac8`
- Files modified: 6
- New files: 3 (including migration script)

Railway will automatically deploy these changes.

---

## 🚂 Running Migration on Railway

You have **3 options** to run the migration on Railway:

### **Option 1: Railway CLI (Recommended)**

This is the easiest and most direct method.

#### Step 1: Install Railway CLI (if not installed)
```bash
# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex

# Or using npm
npm install -g @railway/cli
```

#### Step 2: Login to Railway
```bash
railway login
```

#### Step 3: Link to Your Project
```bash
# Navigate to your project directory
cd path/to/hitech-ai-sales

# Link to Railway project
railway link
```

#### Step 4: Run the Migration
```bash
railway run python add_checkin_sync_tracking.py
```

This will execute the migration script directly on Railway's environment with access to the production database.

---

### **Option 2: Railway Dashboard (One-time Command)**

If you don't want to install the CLI, you can run it via the Railway dashboard.

#### Step 1: Open Railway Dashboard
1. Go to https://railway.app
2. Navigate to your project
3. Click on your service (the one running the FastAPI app)

#### Step 2: Open Shell
1. Click on the **"Settings"** tab
2. Scroll down to **"Service"** section
3. Click **"Open Shell"** or **"Deploy Logs"**
4. Look for a **"Shell"** or **"Terminal"** button

#### Step 3: Run Migration
In the shell, run:
```bash
python add_checkin_sync_tracking.py
```

---

### **Option 3: Add to Startup Script (Automatic)**

Make the migration run automatically on every deployment.

#### Step 1: Create a startup script
Create a file named `railway_startup.sh`:

```bash
#!/bin/bash
echo "🚀 Running Railway startup tasks..."

# Run migration
echo "📊 Running check-in sync tracking migration..."
python add_checkin_sync_tracking.py

# Start the application
echo "🌐 Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### Step 2: Make it executable
```bash
chmod +x railway_startup.sh
```

#### Step 3: Update Railway Start Command
In Railway Dashboard:
1. Go to **Settings** → **Deploy**
2. Find **"Start Command"**
3. Change from:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
   To:
   ```
   bash railway_startup.sh
   ```

#### Step 4: Commit and Push
```bash
git add railway_startup.sh
git commit -m "Add Railway startup script with migration"
git push origin main
```

Railway will automatically redeploy and run the migration.

---

## 🔍 Verify Migration Success

After running the migration, verify it worked:

### Method 1: Check via API
```bash
# Using curl
curl https://your-app.railway.app/api/crm/sync-status

# Should return:
{
  "status": "ok",
  "data": {
    "last_sync": "...",
    "last_checkin_sync": "...",  # ← This should exist
    ...
  }
}
```

### Method 2: Check via Railway Logs
```bash
railway logs
```

Look for:
```
✅ Added last_checkin_sync setting
```
or
```
ℹ️  last_checkin_sync setting already exists
```

### Method 3: Check Settings Page
1. Open your app: `https://your-app.railway.app`
2. Go to **Settings** page
3. Scroll to **"CRM Sync Status"**
4. Should see:
   - Last Comments Sync: [timestamp]
   - Last Check-ins Sync: [timestamp] ← **NEW**
   - Total Check-ins: X check-ins ← **NEW**

---

## 🛠️ Troubleshooting

### Issue: "Module not found" error
**Solution**: Make sure all dependencies are installed
```bash
railway run pip install -r requirements.txt
```

### Issue: "Database locked" error
**Solution**: Stop the running service temporarily
```bash
railway down
railway run python add_checkin_sync_tracking.py
railway up
```

### Issue: Migration runs but no changes
**Solution**: Check if setting already exists
```bash
railway run python -c "
from app.database import AsyncSessionLocal, init_db
from app.models import AppSetting
from sqlalchemy import select
import asyncio

async def check():
    await init_db()
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(AppSetting).where(AppSetting.key == 'last_checkin_sync')
        )
        setting = result.scalar_one_or_none()
        if setting:
            print(f'✅ Setting exists: {setting.value}')
        else:
            print('❌ Setting does not exist')

asyncio.run(check())
"
```

---

## 📋 Quick Reference Commands

### Railway CLI Commands
```bash
# Login
railway login

# Link project
railway link

# Run migration
railway run python add_checkin_sync_tracking.py

# Check logs
railway logs

# Open shell
railway shell

# Check environment variables
railway variables

# Restart service
railway restart
```

---

## 🔐 Important Notes

1. **Database Connection**: The migration script uses the same `DATABASE_URL` environment variable as your app, so it will automatically connect to the correct database.

2. **Idempotent**: The migration is safe to run multiple times. It checks if the setting already exists before adding it.

3. **No Downtime**: This migration doesn't modify table schemas, only adds a row to `app_settings`. Your app can continue running.

4. **Automatic Deployment**: Railway automatically deploys when you push to `main`. The code changes are already live, but the migration needs to be run once.

---

## ✅ Recommended Approach

**For immediate deployment:**
1. Use **Option 1 (Railway CLI)** - fastest and most reliable
2. Run: `railway run python add_checkin_sync_tracking.py`
3. Verify via Settings page

**For future deployments:**
1. Use **Option 3 (Startup Script)** - automatic on every deploy
2. Ensures migrations always run before app starts

---

## 📞 Need Help?

If you encounter issues:

1. **Check Railway Logs**:
   ```bash
   railway logs --tail 100
   ```

2. **Check Database Connection**:
   ```bash
   railway run python -c "from app.database import init_db; import asyncio; asyncio.run(init_db()); print('✅ DB Connected')"
   ```

3. **Manual SQL (Last Resort)**:
   If all else fails, you can manually insert the setting via Railway's database console:
   ```sql
   INSERT INTO app_settings (key, value, updated_at)
   VALUES ('last_checkin_sync', datetime('now'), datetime('now'));
   ```

---

## 🎉 After Migration

Once the migration is complete:

1. ✅ Settings page will show check-in sync data
2. ✅ Manual sync will sync both comments and check-ins
3. ✅ New counts will be displayed for both data types
4. ✅ All data will come from database (not hardcoded)

Your deployment is complete! 🚀

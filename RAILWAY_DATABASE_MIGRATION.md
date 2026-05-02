# 🗄️ Railway Database Migration Guide

## 📊 Your Current Data

- **96 reps** with phone numbers
- **10,022 customers**
- **9,993 conversations**
- **13,560 messages**
- **128,221 CRM comments**
- **5,578 check-ins**

**Database Size**: 82 MB
**Export File**: `railway_database_dump.sql` (88.64 MB)

---

## 🚀 Migration Options

### **Option 1: Railway CLI (Recommended - 10 minutes)**

This is the best way to upload your database to Railway.

#### Step 1: Install Railway CLI

**Windows:**
```bash
# Using npm
npm install -g @railway/cli

# Or using Scoop
scoop install railway
```

**Verify installation:**
```bash
railway --version
```

#### Step 2: Login to Railway

```bash
railway login
```

This will open your browser to authenticate.

#### Step 3: Link to Your Project

```bash
# Navigate to your project folder
cd C:\Users\the_Nerds\Desktop\hitech-ai

# Link to Railway project
railway link
```

Select your `comments` project from the list.

#### Step 4: Upload Database

```bash
# Copy your local database to Railway
railway run python -c "import shutil; shutil.copy('hitech_sales.db', '/app/hitech_sales.db')"
```

**OR** use Railway shell:

```bash
# Open Railway shell
railway shell

# Inside Railway shell, run:
python import_database.py
```

---

### **Option 2: Push Database to GitHub (Easier - 5 minutes)**

Since your database is 82MB and GitHub allows files up to 100MB, we can push it directly.

#### Step 1: Remove Database from .gitignore

Edit `.gitignore` and comment out the database line:

```bash
# *.db
# *.sqlite
# *.sqlite3
# hitech_sales.db
```

#### Step 2: Add and Push Database

```bash
git add hitech_sales.db
git commit -m "Add production database with all data"
git push
```

#### Step 3: Redeploy on Railway

Railway will automatically redeploy and use the database from GitHub.

---

### **Option 3: Use SQL Dump (Alternative)**

If the database file is too large, use the SQL dump.

#### Step 1: Create Import Script

I'll create this for you (see `import_database_from_dump.py` below).

#### Step 2: Push SQL Dump to GitHub

```bash
git add railway_database_dump.sql
git commit -m "Add database SQL dump"
git push
```

#### Step 3: Run Import on Railway

Use Railway shell:

```bash
railway shell
python import_database_from_dump.py
```

---

## 📋 Recommended Approach: Push Database to GitHub

This is the easiest method. Here's the complete process:

### Step 1: Update .gitignore

```bash
# Open .gitignore and comment out these lines:
# *.db
# hitech_sales.db
```

### Step 2: Add Database to Git

```bash
git add hitech_sales.db
git commit -m "Add production database - 96 reps, 10k customers, 9k conversations"
git push
```

### Step 3: Verify on Railway

1. Go to Railway dashboard
2. Check deployment logs
3. Wait for deployment to complete
4. Visit your app URL

### Step 4: Verify Data

Visit these URLs to confirm:
- `https://your-app.railway.app/api/dashboard/summary`
- `https://your-app.railway.app/docs`
- `https://your-app.railway.app/frontend/index.html`

Should show:
- ✅ 96 reps
- ✅ 10,022 customers
- ✅ 9,993 conversations

---

## 🔧 Alternative: Sync from CRM

If you don't want to push the database, you can sync data from CRM on Railway:

### Step 1: SSH into Railway

```bash
railway shell
```

### Step 2: Run Sync Scripts

```bash
# Sync reps and customers
python -c "
import asyncio
from app.database import AsyncSessionLocal
from app.services.crm_client import sync_reps_and_customers

async def sync():
    async with AsyncSessionLocal() as db:
        await sync_reps_and_customers(db)

asyncio.run(sync())
"

# Sync CRM comments
curl -X POST https://your-app.railway.app/api/crm/sync

# Sync check-ins
curl -X POST https://your-app.railway.app/api/checkin/sync?days=90
```

This will take 10-15 minutes but will populate all data from CRM.

---

## ⚡ Quick Start (Recommended)

**Do this now (5 minutes):**

```bash
# 1. Update .gitignore
# Comment out: *.db and hitech_sales.db

# 2. Add database
git add hitech_sales.db

# 3. Commit
git commit -m "Add production database with all data"

# 4. Push
git push

# 5. Wait for Railway to redeploy (2-3 minutes)

# 6. Check your app
# Visit: https://your-app.railway.app/frontend/index.html
```

---

## ✅ Verification Checklist

After migration, verify:

- [ ] Dashboard shows 96 reps (not 5)
- [ ] Inbox shows 9,993 conversations (not 5)
- [ ] Settings shows CRM connected
- [ ] WhatsApp shows connected
- [ ] Rep names are real (not "Alice", "Bob", etc.)
- [ ] Customer data is present
- [ ] Check-ins are visible

---

## 🆘 Troubleshooting

### Database Not Loading?

**Check Railway logs:**
```bash
railway logs
```

Look for:
- ✅ "Application startup complete"
- ✅ "96 reps loaded"
- ❌ "Database error"

### Still Showing 5 Records?

**Possible causes:**
1. Database file not uploaded
2. Railway using old database
3. Seed data overwriting real data

**Solution:**
1. Check if `hitech_sales.db` is in GitHub repo
2. Redeploy on Railway
3. Check logs for errors

### Database Too Large?

If database is >100MB:
1. Use SQL dump instead
2. Or use Railway CLI to upload
3. Or sync from CRM directly

---

## 📊 Database Stats

**Current Database:**
- Size: 82.09 MB
- Tables: 10
- Total Records: ~167,470

**Breakdown:**
- reps: 96
- customers: 10,022
- conversations: 9,993
- messages: 13,560
- crm_comments: 128,221
- checkins: 5,578
- seniors: ~10
- style_samples: ~100
- style_profiles: ~50
- app_settings: ~10

---

## 🎯 Next Steps

1. **Choose migration method** (recommend: Push to GitHub)
2. **Follow steps above**
3. **Verify data on Railway**
4. **Test CRM sync** (should add new data)
5. **Test WhatsApp** (send test message)

---

## 💡 Pro Tips

- **Backup first**: Keep a copy of `hitech_sales.db`
- **Test locally**: Verify database works before pushing
- **Check logs**: Always check Railway logs after deployment
- **Incremental sync**: After initial migration, CRM sync will add new data

---

**Ready to migrate? Follow the Quick Start above!** 🚀

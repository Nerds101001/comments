# 🚀 Quick Start - Run Migration on Railway

## ⚡ Fastest Method (3 Commands)

```bash
# 1. Install Railway CLI (if not installed)
iwr https://railway.app/install.ps1 | iex

# 2. Login and link to your project
railway login
railway link

# 3. Run the migration
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

## ✅ Verify It Worked

Open your app and check the Settings page:
- Should see "Last Check-ins Sync" timestamp
- Should see "Total Check-ins" count
- Manual sync should sync both comments and check-ins

---

## 🔄 Make It Automatic (Optional)

To run migrations automatically on every deployment:

**In Railway Dashboard:**
1. Go to Settings → Deploy
2. Change Start Command to: `bash railway_startup.sh`
3. Save

Now migrations will run automatically before every deployment!

---

## 📚 Full Documentation

- **RAILWAY_MIGRATION_GUIDE.md** - Complete guide with all options
- **DEPLOYMENT_COMPLETE.md** - Full deployment status
- **SETTINGS_PAGE_FIXES.md** - Technical details of all fixes

---

## 🆘 Need Help?

```bash
# Check Railway logs
railway logs

# Open Railway shell
railway shell

# Restart Railway service
railway restart
```

That's it! 🎉

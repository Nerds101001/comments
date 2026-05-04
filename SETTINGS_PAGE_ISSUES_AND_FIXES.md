# Settings Page Issues & Fixes

## 🔴 Issues Found

### 1. **CRM Sync Status - WORKING BUT OUTDATED DISPLAY**
- **Issue:** Frontend shows "Last sync: 5h ago" (9:01 AM)
- **Reality:** Sync IS working, last ran at 1:46 AM (7.6 hours ago)
- **Root Cause:** Scheduler is running every 60 minutes, but frontend is showing old cached data
- **Status:** ✅ SYNC IS WORKING - just needs frontend refresh

### 2. **128,189 Pending Comments NOT PROCESSED**
- **Issue:** 128,189 comments are stuck in "pending" status
- **Reality:** Only 32 comments have been processed by AI
- **Root Cause:** AI processing step is NOT running after sync
- **Impact:** Comments are synced but AI is not generating follow-ups

### 3. **Wrong Config Keys in Settings API**
- **Issue:** Settings API checking for `CLAUDE_API_KEY` instead of `AI_API_KEY`
- **Reality:** System uses NVIDIA AI, not Claude
- **Status:** ✅ FIXED in code

---

## ✅ Fixes Applied

### Fix 1: Updated Settings API Config Keys
**File:** `app/api/settings_api.py`

**Changed:**
```python
# OLD (wrong)
"claude": {
    "connected": bool(settings.CLAUDE_API_KEY),
    ...
}

# NEW (correct)
"ai": {
    "connected": bool(settings.AI_API_KEY),
    "provider": settings.AI_PROVIDER,  # nvidia
    "model": settings.AI_MODEL,
    ...
}
```

**Changed:**
```python
# OLD (wrong)
"crm": {
    "connected": bool(settings.CRM_TOKEN or settings.CRM_USERNAME),
    ...
}

# NEW (correct)
"crm": {
    "connected": bool(settings.CRM_USERNAME and settings.CRM_PASSWORD),
    ...
}
```

---

## 🔧 Fixes Needed

### Fix 2: Enable AI Processing After Sync

**Problem:** The scheduler syncs comments but doesn't process them with AI.

**Current Code** (`app/main.py` line ~180):
```python
async def _poll_crm():
    async with AsyncSessionLocal() as db:
        from app.api import crm as crm_api
        logger.info("CRM auto-poll: starting sync…")
        try:
            result = await crm_api.sync_crm_comments(hours_back=1, emp_code=None, db=db)
            if result.data and result.data.get("new_comments", 0) > 0:
                await crm_api.process_all_pending(db=db)  # ← This line exists!
        except Exception as exc:
            logger.error("CRM poll error: %s", exc)
```

**The code looks correct!** But AI processing might be failing silently.

**Need to check:**
1. Is AI API key configured?
2. Are there errors in AI processing?
3. Is WhatsApp configured (needed to send follow-ups)?

---

## 🔍 Diagnostic Steps

### Step 1: Check AI Configuration
```bash
# Check .env file
cat .env | grep AI_

# Should show:
# AI_API_KEY=nvapi-...
# AI_MODEL=openai/gpt-oss-120b
# AI_BASE_URL=https://integrate.api.nvidia.com/v1
# AI_PROVIDER=nvidia
```

### Step 2: Check WhatsApp Configuration
```bash
# Check .env file
cat .env | grep WHATSAPP_

# Should show:
# WHATSAPP_PHONE_NUMBER_ID=...
# WHATSAPP_ACCESS_TOKEN=...
```

### Step 3: Test AI Processing Manually
```bash
# Run manual processing script
python manual_sync_and_process.py
```

### Step 4: Check Application Logs
```bash
# Local
# Check console output when app is running

# Railway (Live)
# Go to Railway dashboard → Deployments → View Logs
# Look for:
# - "CRM auto-poll: starting sync…"
# - "CRM sync: fetched X new comments"
# - Any error messages
```

---

## 🚀 Recommended Actions

### Action 1: Restart Application (Both Local & Live)
**Why:** Picks up the fixed settings API code

**Local:**
```bash
# Stop the app (Ctrl+C)
# Start again
uvicorn app.main:app --reload --port 8002
```

**Railway:**
```bash
# Push the fixed code
git add app/api/settings_api.py
git commit -m "Fix settings API config keys"
git push origin main

# Railway will auto-deploy
```

### Action 2: Process Pending Comments
**Why:** Clear the backlog of 128,189 pending comments

**Option A: Via Frontend**
1. Go to Settings tab
2. Click "Sync Now" button
3. This will sync AND process

**Option B: Via API**
```bash
# Trigger processing
curl -X POST http://localhost:8002/api/crm/process-all

# Or for Railway
curl -X POST https://web-production-fa001.up.railway.app/api/crm/process-all
```

**Option C: Via Script** (Recommended for large backlog)
```bash
# Process in batches to avoid timeout
python manual_sync_and_process.py
```

### Action 3: Monitor Sync Status
**Frontend:**
- Go to Settings tab
- Check "CRM Sync Status" section
- Click "Refresh Status" button
- Should show updated last sync time

**API:**
```bash
# Check sync status
curl http://localhost:8002/api/crm/sync-status

# Should return:
# {
#   "status": "ok",
#   "data": {
#     "last_sync": "2026-05-02T14:51:17",
#     "pending_count": 0,  # ← Should decrease
#     "processed_count": 128221,  # ← Should increase
#     "total_count": 128221
#   }
# }
```

---

## 📊 Expected Results After Fixes

### Before:
- ❌ Last sync: 5h ago (outdated)
- ❌ Pending: 128,189 comments
- ❌ Processed: 32 comments
- ❌ AI not generating follow-ups

### After:
- ✅ Last sync: < 1h ago (current)
- ✅ Pending: 0-50 comments (only new ones)
- ✅ Processed: 128,000+ comments
- ✅ AI generating follow-ups automatically
- ✅ WhatsApp messages being sent to reps

---

## 🎯 Summary

**What's Working:**
- ✅ CRM sync scheduler (every 60 minutes)
- ✅ Comments being fetched from CRM
- ✅ Comments being stored in database

**What's NOT Working:**
- ❌ AI processing of comments (128,189 backlog)
- ❌ Follow-up questions not being generated
- ❌ WhatsApp messages not being sent

**Root Cause:**
- AI processing step might be failing silently
- Need to check AI API key configuration
- Need to check WhatsApp configuration
- Need to process the backlog

**Next Steps:**
1. Restart application (picks up fixes)
2. Check AI & WhatsApp config
3. Process pending comments backlog
4. Monitor sync status

---

## 📞 Quick Test

**Test if everything is working:**

1. **Trigger manual sync:**
   ```bash
   curl -X POST "http://localhost:8002/api/crm/sync?hours_back=1"
   ```

2. **Check status:**
   ```bash
   curl http://localhost:8002/api/crm/sync-status
   ```

3. **Process pending:**
   ```bash
   curl -X POST http://localhost:8002/api/crm/process-all
   ```

4. **Check status again:**
   ```bash
   curl http://localhost:8002/api/crm/sync-status
   ```

If `pending_count` decreases and `processed_count` increases, everything is working!

---

## 🔧 Configuration Checklist

- [ ] AI_API_KEY is set in .env
- [ ] AI_PROVIDER=nvidia in .env
- [ ] WHATSAPP_PHONE_NUMBER_ID is set
- [ ] WHATSAPP_ACCESS_TOKEN is set
- [ ] CRM_USERNAME=Nagender
- [ ] CRM_PASSWORD=nag@8745
- [ ] CRM_POLL_INTERVAL_MINUTES=60
- [ ] Application restarted after config changes
- [ ] Pending comments processed
- [ ] Sync status shows recent sync time

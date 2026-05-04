# CRM Auto-Sync Configuration & Details

## 🕐 Sync Timing

### Current Configuration:
- **Sync Interval:** Every **60 minutes** (1 hour)
- **Configured in:** `app/config.py`
- **Environment Variable:** `CRM_POLL_INTERVAL_MINUTES=60`

### How to Change:
1. **Local Development:** Edit `.env` file
   ```
   CRM_POLL_INTERVAL_MINUTES=30  # Change to 30 minutes
   ```

2. **Railway (Live):** Update environment variable in Railway dashboard
   - Go to Railway project settings
   - Variables tab
   - Update `CRM_POLL_INTERVAL_MINUTES`
   - Redeploy

---

## 📥 What Gets Synced Automatically

### 1. **CRM Comments** (Primary Sync)
- **Source:** rustx.net CRM API
- **Endpoint:** `/api/Comment/GetPipelineComment/{from_date}/{to_date}/{emp_code}`
- **Frequency:** Every 60 minutes
- **Data Fetched:**
  - Comment ID
  - Employee Code (rep)
  - Company Code (customer)
  - Comment Text (visit notes, remarks)
  - Comment Date
  - Status, Stages, Financial Year

### 2. **Incremental Sync Logic**
- **Smart Sync:** Only fetches NEW comments since last sync
- **Tracks:** Last sync timestamp in database (`app_settings` table)
- **Fallback:** If no last sync time, fetches last 1 hour

### 3. **Per-Rep Sync**
- Loops through ALL active reps in database
- Fetches comments for each rep's `emp_code`
- Maps to local rep and customer records

---

## 🤖 What Happens After Sync

### Automatic AI Processing:
1. **Sync Comments** → Stores new comments with status `pending`
2. **AI Processing** → Automatically processes all pending comments:
   - Summarizes the visit/comment
   - Generates intelligent follow-up question
   - Creates conversation in inbox
   - Sends WhatsApp message to rep (if configured)
   - Updates status to `followup_sent`

### AI Processing Flow:
```
CRM Comment (pending)
    ↓
AI Analyzes
    ↓
Generates Follow-up Question
    ↓
Creates Conversation
    ↓
Sends WhatsApp to Rep
    ↓
Status: followup_sent
    ↓
Rep Replies
    ↓
AI Scores Confidence
    ↓
If ≥88%: Resolved
If <88%: Escalated to Senior/Mukul
```

---

## 📊 Sync Status Monitoring

### Check Sync Status:
**API Endpoint:** `GET /api/crm/sync-status`

**Returns:**
```json
{
  "status": "ok",
  "data": {
    "last_sync": "2026-05-02T14:30:00",
    "pending_count": 5,
    "processed_count": 120,
    "total_count": 125
  }
}
```

### Frontend Display:
- Settings tab → CRM Sync section
- Shows last sync time
- Shows pending/processed counts
- Manual sync button available

---

## 🔄 Manual Sync Options

### 1. **Via Frontend:**
- Go to Settings tab
- Click "Sync Now" button
- Fetches last 24 hours by default

### 2. **Via API:**
```bash
# Sync last 24 hours
POST /api/crm/sync?hours_back=24

# Sync specific rep
POST /api/crm/sync?emp_code=1714

# Incremental sync (since last sync)
POST /api/crm/sync
```

### 3. **Process Pending Comments:**
```bash
POST /api/crm/process-all
```

---

## 🗄️ Database Tables Involved

### 1. **crm_comments**
- Stores all synced CRM comments
- Fields: `crm_comment_id`, `rep_id`, `customer_id`, `raw_text`, `comment_date`
- AI fields: `processed_summary`, `followup_question`, `confidence_score`
- Status: `pending` → `followup_sent` → `resolved` or `escalated`

### 2. **conversations**
- Created automatically from CRM comments
- Links to rep and customer
- Contains AI-generated follow-up questions

### 3. **messages**
- Follow-up questions sent to reps
- Rep replies captured here
- AI confidence scoring

### 4. **app_settings**
- Key: `last_crm_sync`
- Value: ISO timestamp of last successful sync

---

## ⚙️ Configuration Files

### 1. **app/config.py**
```python
CRM_BASE_URL: str = "https://api-crm.rustx.net"
CRM_USERNAME: str = "Nagender"
CRM_PASSWORD: str = "nag@8745"
CRM_POLL_INTERVAL_MINUTES: int = 60  # ← Sync interval
```

### 2. **.env (Local)**
```bash
CRM_BASE_URL=https://api-crm.rustx.net
CRM_USERNAME=Nagender
CRM_PASSWORD=nag@8745
CRM_POLL_INTERVAL_MINUTES=60
```

### 3. **Railway Environment Variables**
```
CRM_BASE_URL=https://api-crm.rustx.net
CRM_USERNAME=Nagender
CRM_PASSWORD=nag@8745
CRM_POLL_INTERVAL_MINUTES=60
```

---

## 🚀 Scheduler Details

### Implementation:
- **Library:** APScheduler (AsyncIOScheduler)
- **Trigger:** IntervalTrigger
- **Job ID:** `crm_poll`
- **Started:** On application startup (`lifespan` function)

### Code Location:
- **File:** `app/main.py`
- **Function:** `_start_scheduler()`
- **Job Function:** `_poll_crm()`

### Scheduler Behavior:
- Runs in background (non-blocking)
- Survives application restarts
- Logs all sync activities
- Error handling: Logs errors but continues running

---

## 📝 Logs to Monitor

### Sync Logs:
```
INFO: CRM poll scheduler started (every 60 min)
INFO: CRM auto-poll: starting sync…
INFO: CRM sync: fetched 5 new comments
INFO: Incremental sync: fetching last 2 hours since 2026-05-02T12:30:00
```

### Error Logs:
```
ERROR: CRM poll error: Connection timeout
WARNING: Could not send WhatsApp follow-up: Invalid phone number
```

---

## 🔧 Troubleshooting

### Sync Not Working?
1. **Check CRM credentials** in environment variables
2. **Check last sync time** via `/api/crm/sync-status`
3. **Check logs** for error messages
4. **Test CRM connection** via `/api/crm/status`
5. **Manual sync** to test: `POST /api/crm/sync?hours_back=1`

### No Comments Being Fetched?
1. **Verify employee codes** in database match CRM
2. **Check date range** - CRM may not have data for that period
3. **Test specific rep** - `POST /api/crm/sync?emp_code=1714`

### AI Not Processing?
1. **Check AI API key** in environment variables
2. **Check pending count** - may be 0 (all processed)
3. **Manual process** - `POST /api/crm/process-all`

---

## 📈 Performance Considerations

### Current Load:
- **96 reps** × **60-minute intervals** = ~96 API calls per hour
- **Incremental sync** reduces load (only new comments)
- **Rate limiting:** 0.3s delay between rep fetches

### Optimization Tips:
1. **Increase interval** if too frequent (e.g., 120 minutes)
2. **Use incremental sync** (default behavior)
3. **Monitor API rate limits** from CRM provider

---

## 🎯 Summary

**What:** Auto-syncs CRM comments every 60 minutes  
**From:** rustx.net CRM API  
**For:** All 96 active reps  
**Processing:** AI automatically processes and sends follow-ups  
**Status:** Tracked in database and visible in frontend  
**Control:** Configurable via environment variable  

**Current Status:**
- ✅ Auto-sync enabled
- ✅ Running every 60 minutes
- ✅ AI processing enabled
- ✅ WhatsApp follow-ups enabled
- ✅ Incremental sync (smart)

---

## 📞 Need Help?

- **Check sync status:** Settings tab in frontend
- **View logs:** Railway deployment logs
- **Test connection:** `/api/crm/status` endpoint
- **Manual sync:** Settings tab → "Sync Now" button

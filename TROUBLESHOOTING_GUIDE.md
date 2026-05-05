# Troubleshooting Guide

## Quick Diagnostic Tools

### 1. Check Database Status
```bash
python check_database_status.py
```
This shows:
- Total comments in database
- Comments by status (pending, resolved, etc.)
- Recent comments
- Last sync time
- Why you might be seeing "0 0"

### 2. Improved Manual Sync
```bash
# Incremental sync (since last sync)
python manual_sync_improved.py

# Sync last 24 hours
python manual_sync_improved.py --hours 24

# Sync last 30 days
python manual_sync_improved.py --hours 720
```

### 3. Reset Comments for Testing
```bash
# Reset last 50 comments
python reset_comments_for_testing.py

# Reset last 100 comments
python reset_comments_for_testing.py --count 100

# Reset ALL comments (careful!)
python reset_comments_for_testing.py --all
```

---

## Issue 1: SMTP Test Failing

### Error
```json
{
    "status": "error",
    "message": "SMTP error: Connection unexpectedly closed: [Errno 104] Connection reset by peer"
}
```

### Solution Applied
✅ **Fixed**: Added SSL context to STARTTLS connection in:
- `app/api/settings_api.py` (line ~213)
- `app/services/email_service.py` (line ~67)

The fix adds proper SSL context:
```python
context = ssl.create_default_context()
server.starttls(context=context)
```

### Testing the Fix
1. Restart your application
2. Go to Settings → Email/SMTP
3. Click "Test connection"
4. You should now see: "✅ Test email sent successfully"

### If Still Failing

#### Check 1: Verify SMTP Settings
```python
# In Railway or your environment, check:
SMTP_HOST=smtp2.hostinger.com
SMTP_PORT=587
SMTP_USER=your-email@domain.com
SMTP_PASSWORD=your-password
```

#### Check 2: Test with Python Directly
```python
import smtplib
import ssl

host = "smtp2.hostinger.com"
port = 587
user = "your-email@domain.com"
password = "your-password"

context = ssl.create_default_context()
server = smtplib.SMTP(host, port, timeout=15)
server.set_debuglevel(1)  # See detailed output
server.ehlo()
server.starttls(context=context)
server.ehlo()
server.login(user, password)
print("✅ Success!")
server.quit()
```

#### Check 3: Railway Network Issues
Railway might block outbound SMTP. Try:
1. Check Railway logs for network errors
2. Try port 465 (SSL) instead of 587 (STARTTLS)
3. Contact Railway support about SMTP restrictions

#### Check 4: SMTP Provider Issues
Some providers require:
- App-specific passwords (not your regular password)
- Whitelisting Railway's IP addresses
- Enabling "less secure apps" or "SMTP access"

---

## Issue 2: Sync Shows "0 0"

### Symptom
```
Batch 1: Processing up to 50 comments...
  ✅ Processed: 0, Errors: 0
```

### Diagnosis Steps

#### Step 1: Check Database
```bash
python check_database_status.py
```

Look for:
- **Total comments**: If 0, you need to sync first
- **Pending count**: If 0, all comments are already processed
- **Last sync time**: When was the last sync?

#### Step 2: Check What's Pending
```bash
# Via API
curl http://localhost:8002/api/crm/comments?status=pending&limit=10

# Or via Python
python -c "
import asyncio
from app.database import AsyncSessionLocal
from app.models import CRMComment
from sqlalchemy import select, func

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(func.count(CRMComment.id))
            .where(CRMComment.resolution_status == 'pending')
        )
        print(f'Pending: {result.scalar()}')

asyncio.run(check())
"
```

### Common Causes & Solutions

#### Cause 1: No Comments in Database
**Solution**: Run a full sync
```bash
python manual_sync_improved.py --hours 720  # Last 30 days
```

#### Cause 2: All Comments Already Processed
**Solution**: Either wait for new comments, or reset for testing
```bash
python reset_comments_for_testing.py --count 50
```

#### Cause 3: Incremental Sync Window Too Small
The default incremental sync only fetches comments since last sync (could be just 1 hour).

**Solution**: Force a larger time window
```bash
python manual_sync_improved.py --hours 168  # Last 7 days
```

#### Cause 4: CRM API Not Returning Data
**Check CRM connection**:
```bash
curl http://localhost:8002/api/crm/status
```

**Check CRM credentials**:
```bash
# In .env or Railway
CRM_BASE_URL=https://api-crm.rustx.net
CRM_USERNAME=your-username
CRM_PASSWORD=your-password
```

**Test CRM API directly**:
```python
import asyncio
from app.services import crm_client

async def test():
    # Test connection
    result = await crm_client.test_connection()
    print(f"Connected: {result['connected']}")
    
    # Try fetching comments
    comments = await crm_client.get_pipeline_comments(
        emp_code="YOUR_EMP_CODE",
        from_date="01-01-2025",
        to_date="31-01-2025"
    )
    print(f"Comments: {len(comments)}")
    if comments:
        print(f"Sample: {comments[0]}")

asyncio.run(test())
```

#### Cause 5: Date Format Issues
The CRM API expects dates in `dd-mm-yyyy` format. Check logs to see what dates are being sent.

**Add logging**:
```python
# In app/api/crm.py, line ~145
logger.info(f"Syncing: from_date={from_date}, to_date={to_date}")
```

---

## Issue 3: Comments Not Processing

### Symptom
Comments are synced (pending count > 0) but process-all returns 0 processed.

### Diagnosis

#### Check 1: AI API Working?
```bash
curl http://localhost:8002/api/settings/test/ai
```

Should return:
```json
{
    "status": "connected",
    "message": "NVIDIA openai/gpt-oss-120b OK"
}
```

#### Check 2: Process One Comment Manually
```bash
# Get a pending comment ID
curl http://localhost:8002/api/crm/comments?status=pending&limit=1

# Process it
curl -X POST http://localhost:8002/api/crm/comments/123/process
```

Check the response for errors.

#### Check 3: Check Logs
```bash
# Railway
railway logs

# Local
# Check console output for errors
```

### Common Errors

#### Error: "AI API key not set"
**Solution**: Set AI_API_KEY in environment
```bash
AI_API_KEY=nvapi-xxxxx
AI_PROVIDER=nvidia
AI_MODEL=openai/gpt-oss-120b
```

#### Error: "Rep not found"
**Solution**: Ensure reps are in database
```bash
curl http://localhost:8002/api/settings/team
```

If empty, add reps via the UI or API.

#### Error: "Customer not found"
This is OK - customer is optional. The comment will still process.

---

## Issue 4: WhatsApp Not Sending

### Symptom
Comments are processed but follow-up questions not sent to reps.

### Diagnosis

#### Check 1: WhatsApp Configured?
```bash
curl http://localhost:8002/api/settings/test/whatsapp
```

#### Check 2: Rep Has Phone Number?
```bash
curl http://localhost:8002/api/settings/team
```

Check that each rep has a `phone` field with country code (e.g., "919876543210").

#### Check 3: WhatsApp API Logs
Check Railway logs for WhatsApp API errors:
```
Could not send WhatsApp follow-up: ...
```

### Solutions

#### Solution 1: Set WhatsApp Credentials
```bash
WHATSAPP_PHONE_NUMBER_ID=123456789
WHATSAPP_ACCESS_TOKEN=EAABxxxxxxx
```

#### Solution 2: Add Phone Numbers to Reps
Via API:
```bash
curl -X PUT http://localhost:8002/api/settings/team/REP_ID \
  -H "Content-Type: application/json" \
  -d '{"phone": "919876543210"}'
```

Via UI: Settings → Team → Edit Rep → Add Phone

---

## Monitoring & Debugging

### Enable Debug Logging
```python
# In app/main.py or app/config.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Sync Status Regularly
```bash
curl http://localhost:8002/api/crm/sync-status
```

### Monitor Processing
```bash
# Watch pending count
watch -n 5 'curl -s http://localhost:8002/api/crm/sync-status | jq .data.pending_count'
```

### Check Recent Comments
```bash
curl http://localhost:8002/api/crm/comments?limit=10
```

---

## Quick Reference

### API Endpoints
```bash
# Status
GET  /api/crm/sync-status
GET  /api/crm/status

# Sync
POST /api/crm/sync
POST /api/crm/sync?hours_back=24

# Process
POST /api/crm/process-all
POST /api/crm/comments/{id}/process

# List
GET  /api/crm/comments
GET  /api/crm/comments?status=pending
GET  /api/crm/comments?status=pending&limit=100

# Test
POST /api/settings/test/smtp
POST /api/settings/test/crm
POST /api/settings/test/whatsapp
POST /api/settings/test/ai
```

### Database Queries
```python
import asyncio
from app.database import AsyncSessionLocal
from app.models import CRMComment
from sqlalchemy import select, func

async def query():
    async with AsyncSessionLocal() as db:
        # Count by status
        for status in ["pending", "followup_sent", "resolved"]:
            result = await db.execute(
                select(func.count(CRMComment.id))
                .where(CRMComment.resolution_status == status)
            )
            print(f"{status}: {result.scalar()}")

asyncio.run(query())
```

---

## Getting Help

### Logs to Check
1. **Railway logs**: `railway logs`
2. **Application logs**: Check console output
3. **Database**: Use `check_database_status.py`
4. **API responses**: Use curl with `-v` flag

### Information to Provide
When asking for help, include:
1. Output of `check_database_status.py`
2. Output of `manual_sync_improved.py`
3. Relevant error messages from logs
4. Environment (Railway, local, etc.)
5. What you've already tried

### Common Commands
```bash
# Full diagnostic
python check_database_status.py
python manual_sync_improved.py --hours 24

# Test connections
curl http://localhost:8002/api/settings/test/smtp
curl http://localhost:8002/api/settings/test/crm
curl http://localhost:8002/api/settings/test/ai

# Check status
curl http://localhost:8002/api/crm/sync-status

# Force sync
curl -X POST http://localhost:8002/api/crm/sync?hours_back=168

# Process
curl -X POST http://localhost:8002/api/crm/process-all
```

# SMTP and Sync Issues Analysis

## Issue 1: SMTP Test Failing with "Connection reset by peer"

### Error Message
```json
{
    "status": "error",
    "message": "SMTP error: Connection unexpectedly closed: [Errno 104] Connection reset by peer",
    "data": null
}
```

### Root Causes

#### 1. **Missing SSL Context for Port 587**
The code at `app/api/settings_api.py` line 213-219 attempts STARTTLS on port 587 but **does NOT create an SSL context**:

```python
if smtp_port == 587:
    server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
    server.ehlo()
    server.starttls()  # ❌ No SSL context provided!
    server.ehlo()
    server.login(smtp_user, smtp_password)
```

**Problem**: Many modern SMTP servers (especially Gmail, Hostinger, etc.) require a proper SSL context for STARTTLS. Without it, the connection gets reset.

**Solution**: Add SSL context like this:
```python
if smtp_port == 587:
    context = ssl.create_default_context()
    server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
    server.ehlo()
    server.starttls(context=context)  # ✅ Pass SSL context
    server.ehlo()
    server.login(smtp_user, smtp_password)
```

#### 2. **Potential Firewall/Network Issues**
- Railway deployment might have network restrictions
- SMTP server might be blocking connections from Railway's IP range
- Port 587 might be blocked by Railway's firewall

#### 3. **SMTP Server Configuration**
- Some SMTP servers require specific authentication methods
- The server might require OAuth2 instead of password authentication
- The server might have rate limiting or security policies

### Recommended Fixes

#### Fix 1: Add SSL Context (Primary Fix)
```python
# In app/api/settings_api.py, line ~213
if smtp_port == 587:
    context = ssl.create_default_context()
    server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
    server.ehlo()
    server.starttls(context=context)  # Add context here
    server.ehlo()
    server.login(smtp_user, smtp_password)
    server.send_message(msg)
    server.quit()
```

#### Fix 2: Add Better Error Handling and Logging
```python
try:
    if smtp_port == 587:
        context = ssl.create_default_context()
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
        logger.info(f"Connected to {smtp_host}:{smtp_port}")
        
        server.ehlo()
        logger.info("EHLO successful")
        
        server.starttls(context=context)
        logger.info("STARTTLS successful")
        
        server.ehlo()
        logger.info("Second EHLO successful")
        
        server.login(smtp_user, smtp_password)
        logger.info("Login successful")
        
        server.send_message(msg)
        logger.info("Message sent")
        
        server.quit()
        logger.info("Connection closed")
except Exception as e:
    logger.error(f"SMTP error at step: {e}", exc_info=True)
    return StatusResponse(status="error", message=f"SMTP error: {str(e)}")
```

#### Fix 3: Try Alternative Connection Method
Some servers work better with a different approach:
```python
if smtp_port == 587:
    context = ssl.create_default_context()
    # Try with local_hostname specified
    server = smtplib.SMTP(smtp_host, smtp_port, timeout=15, local_hostname='localhost')
    server.set_debuglevel(1)  # Enable debug output
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    server.login(smtp_user, smtp_password)
    server.send_message(msg)
    server.quit()
```

---

## Issue 2: "0 0" After Sync Completion

### What You're Seeing
After running `manual_sync_and_process.py`, you see:
```
Batch 1: Processing up to 50 comments...
  ✅ Processed: 0, Errors: 0
```

### Root Causes

#### 1. **No Pending Comments to Process**
The most likely reason is that there are **no comments with `resolution_status = "pending"`** in the database.

Check this by looking at `app/api/crm.py` line 367-371:
```python
result = await db.execute(
    select(CRMComment)
    .where(CRMComment.resolution_status == "pending")
    .order_by(CRMComment.created_at.asc())
    .limit(50)
)
pending = result.scalars().all()
```

If `pending` is empty, then `processed = 0` and `errors = 0`.

#### 2. **Sync Not Fetching New Comments**
Looking at `app/api/crm.py` line 145-150, the sync might not be finding new comments because:

- **Incremental sync window is too small**: If `hours_back=1`, it only fetches comments from the last hour
- **CRM API not returning data**: The CRM API might not have new comments in the time window
- **Date format mismatch**: The CRM expects `dd-mm-yyyy` format, which might not match the data

#### 3. **Comments Already Processed**
If you've run the script before, all comments might already have `resolution_status != "pending"` (e.g., "resolved", "followup_sent", "escalated").

### Diagnostic Steps

#### Step 1: Check Database Directly
Run this Python script to see what's in the database:

```python
import asyncio
from app.database import AsyncSessionLocal
from app.models import CRMComment
from sqlalchemy import select, func

async def check_db():
    async with AsyncSessionLocal() as db:
        # Count total comments
        total = await db.execute(select(func.count(CRMComment.id)))
        print(f"Total comments: {total.scalar()}")
        
        # Count by status
        for status in ["pending", "followup_sent", "resolved", "escalated"]:
            count = await db.execute(
                select(func.count(CRMComment.id))
                .where(CRMComment.resolution_status == status)
            )
            print(f"  {status}: {count.scalar()}")
        
        # Show last 5 comments
        recent = await db.execute(
            select(CRMComment)
            .order_by(CRMComment.created_at.desc())
            .limit(5)
        )
        print("\nLast 5 comments:")
        for c in recent.scalars().all():
            print(f"  ID: {c.id}, Status: {c.resolution_status}, Date: {c.created_at}")

asyncio.run(check_db())
```

#### Step 2: Force Full Sync
Modify `manual_sync_and_process.py` to force a full sync:

```python
# In Step 2, change:
resp = await client.post(f"{API_BASE}/api/crm/sync")

# To:
resp = await client.post(f"{API_BASE}/api/crm/sync?hours_back=720")  # Last 30 days
```

#### Step 3: Check CRM API Response
Add logging to see what the CRM API returns:

```python
# In app/services/crm_client.py, add logging to get_pipeline_comments
logger.info(f"CRM API returned {len(comments)} comments for {emp_code}")
logger.debug(f"Sample comment: {comments[0] if comments else 'None'}")
```

### Recommended Fixes

#### Fix 1: Add Verbose Logging to Sync
```python
# In app/api/crm.py, around line 145
logger.info(f"Syncing CRM: hours_back={hours_back}, from={from_date}, to={to_date}")
logger.info(f"Processing {len(target_reps)} reps")

for rep in target_reps:
    comments = await crm_client.get_pipeline_comments(
        emp_code=rep.emp_code,
        from_date=from_date,
        to_date=to_date,
    )
    logger.info(f"Rep {rep.name} ({rep.emp_code}): {len(comments)} comments from CRM")
    
    for raw in comments:
        # ... existing code ...
        logger.debug(f"Processing comment: {crm_id}, status: {comment.resolution_status}")
```

#### Fix 2: Add Status Check to Manual Script
```python
# In manual_sync_and_process.py, after Step 1
print("\nDetailed Status:")
try:
    resp = await client.get(f"{API_BASE}/api/crm/comments?status=pending&limit=10")
    resp.raise_for_status()
    pending_comments = resp.json()
    print(f"  Sample pending comments: {len(pending_comments)}")
    if pending_comments:
        print(f"  First pending: ID={pending_comments[0].get('id')}, Text={pending_comments[0].get('raw_text')[:50]}...")
except Exception as e:
    print(f"  ❌ Error fetching pending: {e}")
```

#### Fix 3: Reset Comment Status for Testing
If you want to reprocess comments for testing:

```python
import asyncio
from app.database import AsyncSessionLocal
from app.models import CRMComment
from sqlalchemy import select

async def reset_comments():
    async with AsyncSessionLocal() as db:
        # Reset last 50 comments to pending
        result = await db.execute(
            select(CRMComment)
            .order_by(CRMComment.created_at.desc())
            .limit(50)
        )
        comments = result.scalars().all()
        
        for c in comments:
            c.resolution_status = "pending"
            c.followup_sent = False
            c.followup_sent_at = None
        
        await db.commit()
        print(f"Reset {len(comments)} comments to pending")

asyncio.run(reset_comments())
```

---

## Summary

### SMTP Issue
**Root Cause**: Missing SSL context for STARTTLS on port 587  
**Fix**: Add `context = ssl.create_default_context()` and pass it to `starttls(context=context)`

### Sync "0 0" Issue
**Root Cause**: No pending comments in database (either already processed or not synced)  
**Fix**: 
1. Check database to confirm comment counts
2. Force full sync with `hours_back=720` (30 days)
3. Add verbose logging to see what's happening
4. Verify CRM API is returning data

### Next Steps
1. Apply the SMTP SSL context fix
2. Run the diagnostic script to check database status
3. Force a full sync to get more comments
4. Add logging to understand the flow better

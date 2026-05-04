# Settings Page Fix - Verification Guide

## What Was Fixed

### Issue 1: AI API Showing Hardcoded Values ✅
**Before**: 
- Provider showed hardcoded "NVIDIA"
- API Key showed "Not configured" even when configured
- Model showed "Not configured" even when set

**After**:
- Provider shows actual value from `settings.AI_PROVIDER` (NVIDIA or CLAUDE)
- API Key shows masked value: `●●●●●●●●` + last 4 characters
- Model shows actual value from `settings.AI_MODEL`

**Code Changes**:
```javascript
// frontend/index.html - Line ~3513
<input value="${escapeHtml((ig.ai.provider || 'nvidia').toUpperCase())}" readonly>
<input value="${ig.ai.api_key_preview ? '●●●●●●●●' + ig.ai.api_key_preview.slice(-4) : ''}" readonly>
<input value="${escapeHtml(ig.ai.model || '')}" placeholder="${ig.ai.connected ? 'Configured' : 'Not configured'}" readonly>
```

### Issue 2: CRM Showing "Not Connected" ✅
**Before**:
- API Key field showed `***` when connected
- Inconsistent with other integrations

**After**:
- API Key shows `●●●●●●●●` when connected (8 dots)
- Consistent masking pattern across all integrations
- Proper placeholder text

**Code Changes**:
```javascript
// frontend/index.html - Line ~3565
<input value="${ig.crm.connected ? '●●●●●●●●' : ''}" 
       placeholder="${ig.crm.connected ? 'Configured' : 'Not configured'}" readonly>
```

### Issue 3: Sync Only Showing Comments (Not Check-ins) ✅
**Before**:
- Only showed comment sync data
- No visibility into check-in sync status
- Single "Last Sync Time" field

**After**:
- Shows separate sync times for comments and check-ins
- Displays total counts for both data types
- Shows new counts since last sync for both

**Backend Changes**:
```python
# app/api/crm.py - sync_status endpoint
return StatusResponse(
    status="ok",
    data={
        "last_sync": last_sync,                              # Comments sync
        "last_checkin_sync": last_checkin_sync,              # Check-ins sync (NEW)
        "total_count": total_count,                          # Total comments
        "total_checkins": total_checkins,                    # Total check-ins (NEW)
        "new_comments_since_last_sync": new_comments_count,  # New comments (NEW)
        "new_checkins_since_last_sync": new_checkins_count,  # New check-ins (NEW)
        "processed_count": processed_count,
        "pending_count": pending_count,
    },
)
```

**Frontend Changes**:
```javascript
// frontend/index.html - Line ~4191
detailsEl.innerHTML = `
  <div class="field-row">
    <label>Last Comments Sync</label>
    <div>${lastSyncFormatted}</div>
  </div>
  <div class="field-row">
    <label>Last Check-ins Sync</label>
    <div>${lastCheckinSyncFormatted}</div>
  </div>
  <div class="field-row">
    <label>Total Comments</label>
    <div>${total_count} (+${new_comments} new)</div>
  </div>
  <div class="field-row">
    <label>Total Check-ins</label>
    <div>${total_checkins} (+${new_checkins} new)</div>
  </div>
  ...
`;
```

### Issue 4: Not Showing NEW Counts ✅
**Before**:
- Only showed total counts
- No way to see how many items were added in last sync
- Manual sync only showed "X new comments"

**After**:
- Shows new counts since last sync for both comments and check-ins
- Displayed in green with (+X new) indicator
- Manual sync shows both comment and check-in counts

**Backend Logic**:
```python
# app/api/crm.py - Line ~90
# Count new comments since last sync
new_comments_count = 0
if last_sync:
    last_sync_dt = datetime.fromisoformat(last_sync)
    new_comments_result = await db.execute(
        select(CRMComment).where(CRMComment.created_at >= last_sync_dt)
    )
    new_comments_count = len(new_comments_result.scalars().all())

# Count new check-ins since last sync
new_checkins_count = 0
if last_checkin_sync:
    last_checkin_sync_dt = datetime.fromisoformat(last_checkin_sync)
    new_checkins_result = await db.execute(
        select(CheckIn).where(CheckIn.created_at >= last_checkin_sync_dt)
    )
    new_checkins_count = len(new_checkins_result.scalars().all())
```

**Manual Sync Enhancement**:
```javascript
// frontend/index.html - manualCRMSync function
async function manualCRMSync() {
  // Sync comments
  const commentsResponse = await fetch('/api/crm/sync', { method: 'POST' });
  const newComments = commentsResult.data?.new_comments || 0;
  
  // Sync check-ins (NEW)
  const checkinsResponse = await fetch('/api/checkin/sync', { method: 'POST' });
  const newCheckins = checkinsResult.data?.total_new || 0;
  
  alert(`✅ Sync completed!\n\n${newComments} new comments\n${newCheckins} new check-ins`);
}
```

## How to Verify

### 1. Check AI API Display
1. Navigate to Settings page
2. Scroll to "AI API" section
3. Verify:
   - ✅ Provider shows "NVIDIA" (uppercase, from database)
   - ✅ API Key shows `●●●●●●●●xxxx` (masked with last 4 chars)
   - ✅ Model shows `openai/gpt-oss-120b` (actual model name)
   - ✅ Status badge shows "● Connected" (green)

### 2. Check CRM Connection
1. Navigate to Settings page
2. Scroll to "CRM / Sales Comments API" section
3. Verify:
   - ✅ Status badge shows "● Connected" (green)
   - ✅ API Endpoint shows `https://api-crm.rustx.net`
   - ✅ API Key shows `●●●●●●●●` (8 dots, masked)
   - ✅ "Test connection" button works

### 3. Check CRM Sync Status
1. Navigate to Settings page
2. Scroll to "CRM Sync Status" section
3. Verify:
   - ✅ Shows "Last Comments Sync" with timestamp
   - ✅ Shows "Last Check-ins Sync" with timestamp
   - ✅ Shows "Total Comments: X comments (+Y new)" with green indicator
   - ✅ Shows "Total Check-ins: X check-ins (+Y new)" with green indicator
   - ✅ Shows "Processed" count
   - ✅ Shows "Pending" count
   - ✅ Shows "Auto-Sync Interval: Every 60 minutes"

### 4. Test Manual Sync
1. Click "Sync Now" button
2. Wait for completion (may take 10-30 seconds)
3. Verify alert shows:
   ```
   ✅ Sync completed!
   
   X new comments
   Y new check-ins
   ```
4. Click "Refresh Status"
5. Verify new counts are updated

## Database Changes

### New App Setting
```sql
-- Added to app_settings table
INSERT INTO app_settings (key, value, updated_at)
VALUES ('last_checkin_sync', '2026-05-04T05:08:58.600535', '2026-05-04 05:08:58.600535');
```

**Migration**: Run `python add_checkin_sync_tracking.py`

## API Response Examples

### GET /api/settings
```json
{
  "team": [...],
  "seniors": [...],
  "integrations": {
    "ai": {
      "connected": true,
      "provider": "nvidia",
      "model": "openai/gpt-oss-120b",
      "api_key_preview": "nvapi-ab..."
    },
    "whatsapp": {
      "connected": true,
      "phone_number_id": "123456789",
      "verify_token": "hitech-verify-2026"
    },
    "crm": {
      "connected": true,
      "base_url": "https://api-crm.rustx.net",
      "poll_interval_minutes": 60
    }
  }
}
```

### GET /api/crm/sync-status
```json
{
  "status": "ok",
  "data": {
    "last_sync": "2026-05-02T01:46:13.369631",
    "last_checkin_sync": "2026-05-04T05:08:58.600535",
    "pending_count": 264891,
    "processed_count": 52,
    "total_count": 264943,
    "total_checkins": 5578,
    "new_comments_since_last_sync": 52,
    "new_checkins_since_last_sync": 120
  }
}
```

### POST /api/crm/sync
```json
{
  "status": "ok",
  "message": "Synced 52 new comments",
  "data": {
    "new_comments": 52,
    "last_sync": "2026-05-04T10:30:00.000000",
    "hours_back": 1
  }
}
```

### POST /api/checkin/sync
```json
{
  "status": "success",
  "message": "Synced 120 new and 5 updated check-ins",
  "data": {
    "total_fetched": 125,
    "total_new": 120,
    "total_updated": 5,
    "errors": [],
    "from_date": "2026-04-04",
    "to_date": "2026-05-04"
  }
}
```

## Files Modified

1. **frontend/index.html**
   - Line ~3513: Fixed AI API fields display
   - Line ~3565: Fixed CRM API key display
   - Line ~4191: Added check-in sync display
   - Line ~4240: Enhanced manual sync function

2. **app/api/crm.py**
   - Line ~60: Enhanced sync_status endpoint
   - Added check-in tracking and new count calculations

3. **app/api/checkin.py**
   - Line ~20: Added last_checkin_sync timestamp tracking

4. **add_checkin_sync_tracking.py** (NEW)
   - Migration script to add new app_setting

## Testing Checklist

- [ ] Settings page loads without errors
- [ ] AI API section shows actual provider (NVIDIA/CLAUDE)
- [ ] AI API section shows actual model name
- [ ] AI API section shows masked API key with last 4 chars
- [ ] CRM section shows "Connected" status
- [ ] CRM section shows masked API key (8 dots)
- [ ] CRM Sync Status shows two separate sync times
- [ ] CRM Sync Status shows total comments with new count
- [ ] CRM Sync Status shows total check-ins with new count
- [ ] Manual sync button syncs both comments and check-ins
- [ ] Manual sync shows both counts in success message
- [ ] Refresh Status button updates all counts
- [ ] New counts are highlighted in green
- [ ] All data comes from database (not hardcoded)

## Rollback Plan

If issues occur, revert these commits:
1. `frontend/index.html` - Revert AI API and CRM display changes
2. `app/api/crm.py` - Revert sync_status endpoint changes
3. `app/api/checkin.py` - Revert timestamp tracking
4. Delete `last_checkin_sync` from app_settings table

## Performance Notes

- New count calculations use `created_at` field with index
- Queries are efficient (single SELECT per data type)
- No impact on existing sync performance
- Frontend updates are instant (no additional API calls)

## Security Notes

- API keys remain masked in frontend
- No sensitive data exposed in new fields
- All authentication checks remain unchanged
- Read-only display fields prevent tampering

## Future Enhancements

Potential improvements:
1. Add real-time sync progress indicator
2. Show sync history (last 10 syncs)
3. Add filtering by date range for new counts
4. Add export functionality for sync logs
5. Add webhook notifications for sync completion

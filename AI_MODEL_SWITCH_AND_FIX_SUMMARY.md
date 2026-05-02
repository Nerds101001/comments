# AI Model Switch & Inbox Fix Summary

## Changes Made

### 1. Switched from Claude to NVIDIA AI Model

**Configuration Updates:**
- Updated `app/config.py`:
  - Replaced `CLAUDE_API_KEY`, `CLAUDE_MODEL`, `CLAUDE_API_URL` with:
    - `AI_API_KEY` - NVIDIA API key
    - `AI_MODEL` - `openai/gpt-oss-120b`
    - `AI_BASE_URL` - `https://integrate.api.nvidia.com/v1`
    - `AI_PROVIDER` - `nvidia`

- Updated `.env`:
  ```env
  AI_API_KEY=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
  AI_MODEL=openai/gpt-oss-120b
  AI_BASE_URL=https://integrate.api.nvidia.com/v1
  AI_PROVIDER=nvidia
  ```

**AI Brain Service Updates (`app/services/ai_brain.py`):**
- Replaced `_call_claude()` function with `_call_ai()` that uses NVIDIA's OpenAI-compatible API
- Updated all AI function calls to use the new `_call_ai()` method:
  - `generate_nudge()`
  - `generate_senior_briefing()`
  - `generate_senior_reply()`
  - `evaluate_confidence()`
  - `process_crm_comment()`
  - `generate_followup_question()`

**API Format:**
The new implementation uses OpenAI-compatible format:
```python
{
    "model": "openai/gpt-oss-120b",
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 1,
    "top_p": 1,
    "max_tokens": max_tokens,
    "stream": False
}
```

The response includes optional `reasoning_content` which is logged for debugging.

### 2. Fixed Blank Dashboard/Inbox/Command Centre

**Problem Identified:**
- Database had 9,309 conversations (created from CRM comments)
- Frontend was trying to load all 9,309 conversations at once
- This caused timeout/performance issues making tabs appear blank

**Solution Implemented:**
- Added pagination to `/api/conversations` endpoint in `app/api/conversations.py`:
  - `limit` parameter (default: 100, max: 500)
  - `offset` parameter (default: 0)
  - Conversations ordered by `updated_at DESC` (most recent first)

**API Usage:**
```
GET /api/conversations?limit=100&offset=0
GET /api/conversations?handler=ai&limit=50
```

### 3. Database Status

**Current State:**
- **96 Reps** (sales team members)
- **10,022 Customers** (companies)
- **9,304 CRM Comments** (all linked to conversations)
- **9,309 Conversations** (5 seed + 9,304 from CRM)
- **9,309 Messages** (one per conversation from CRM comments)

**Data Flow:**
1. CRM comments fetched from rustx.net API
2. Each comment creates a Conversation
3. Each conversation has at least 1 Message (the CRM visit note)
4. All conversations appear in Inbox with handler="ai"

## Testing

### Test API:
```bash
# Test conversations endpoint with pagination
python test_api_conversations.py

# Check database counts
python check_conv_status.py

# List all data
python list_all_data.py
```

### Access Application:
- **Backend API**: http://localhost:8002
- **API Docs**: http://localhost:8002/docs
- **Frontend**: http://localhost:8002/frontend/index.html

## Next Steps

### Frontend Updates Needed:
1. Update frontend to use pagination when loading conversations
2. Implement infinite scroll or "Load More" button
3. Update hardcoded Claude API references in frontend (lines 1957, 2140, 2202)
4. Consider using backend API endpoints instead of direct AI calls from frontend

### Recommended Frontend Changes:
```javascript
// Instead of loading all conversations at once:
const convsRes = await fetch('/api/conversations');

// Load with pagination:
const convsRes = await fetch('/api/conversations?limit=100&offset=0');

// For infinite scroll, load more:
const moreConvs = await fetch(`/api/conversations?limit=100&offset=${currentOffset}`);
```

### Performance Optimization:
- Current: Returns 100 most recent conversations by default
- Frontend can load more as user scrolls
- Filters (handler type) still work with pagination

## Files Modified

1. `app/config.py` - AI configuration
2. `.env` - Environment variables
3. `app/services/ai_brain.py` - AI service implementation
4. `app/api/conversations.py` - Added pagination

## Files Created

1. `create_conversations_from_crm.py` - Script to create conversations from CRM
2. `check_conv_status.py` - Database status checker
3. `test_api_conversations.py` - API testing script
4. `AI_MODEL_SWITCH_AND_FIX_SUMMARY.md` - This file

## Notes

- Server is running on port 8002 (not 8000 or 8001 to avoid Laravel conflict)
- Auto-sync runs every 60 minutes to fetch new CRM comments
- All CRM comments are now visible in Inbox as conversations
- AI model switched to NVIDIA's GPT-OSS-120B
- Pagination prevents frontend from hanging on large datasets

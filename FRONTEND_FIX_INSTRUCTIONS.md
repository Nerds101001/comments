# Frontend Fix Instructions

## Problem
The frontend is still calling Claude API directly, causing CORS errors:
```
Access to fetch at 'https://api.anthropic.com/v1/messages' from origin 'http://localhost:8002' 
has been blocked by CORS policy
```

## Solution
Replace all direct AI API calls with backend API endpoints.

## Changes Made

### 1. Updated `generateNudge()` function
**Before:** Called Claude API directly with full prompt
**After:** Calls `/api/conversations/{conv_id}/generate-nudge` endpoint

```javascript
async function generateNudge(conv, advisoryOnly = false) {
  const response = await fetch(`/api/conversations/${conv.id}/generate-nudge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" }
  });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API error ${response.status}: ${error}`);
  }
  
  const data = await response.json();
  return data.text;
}
```

### 2. Updated `handleGenerateNudge()` function
**Changes:**
- Backend now creates the message in database
- Frontend reloads conversation data after generation
- Proper error handling with finally block

## Remaining Updates Needed

### Senior Functions (Lines ~2098-2220)
These still call Claude API directly and need to be updated:

1. **`generateSeniorBriefing()`** - Should call `/api/conversations/{conv_id}/forward-to-senior/{senior_id}`
2. **`generateSeniorReply()`** - Should call `/api/conversations/{conv_id}/generate-senior-reply`

### Settings Page
Update AI configuration display:
- Change "Claude API" to "NVIDIA AI"  
- Update model name from "claude-sonnet-4" to "openai/gpt-oss-120b"
- Update API provider label

## Testing

After updates, test:
1. Click "Generate AI Nudge" button - should work without CORS errors
2. Check browser console - no more Anthropic API errors
3. Verify messages appear in conversation
4. Test senior escalation flow

## Backend Endpoints Available

```
POST /api/conversations/{conv_id}/generate-nudge
POST /api/conversations/{conv_id}/generate-senior-reply  
POST /api/conversations/{conv_id}/forward-to-senior/{senior_id}
POST /api/conversations/{conv_id}/take-over
POST /api/conversations/{conv_id}/return-to-ai
POST /api/conversations/{conv_id}/approve-draft
POST /api/conversations/{conv_id}/escalate-to-mukul
POST /api/conversations/{conv_id}/resolve
```

All AI generation now uses NVIDIA's GPT-OSS-120B model through the backend.

# AI Knowledge Base - Setup Complete! 🎉

## What Was Implemented:

### 1. ✅ AI Knowledge Base Database Table
- **Table**: `ai_knowledge_base`
- **Fields**:
  - `category`: example_nudge, product_info, terminology, guideline
  - `title`: Short title for the entry
  - `content`: The actual knowledge/example
  - `language`: all, hinglish_80, english_only, etc.
  - `priority`: 1-10 (higher = more important)
  - `is_active`: Enable/disable entries
  - `created_by`: Who added it
  - Timestamps: created_at, updated_at

### 2. ✅ API Endpoints Created
**Base URL**: `/api/knowledge`

- `GET /api/knowledge/entries` - List all knowledge entries (with filters)
- `GET /api/knowledge/entries/{id}` - Get single entry
- `POST /api/knowledge/entries` - Create new entry
- `PUT /api/knowledge/entries/{id}` - Update entry
- `DELETE /api/knowledge/entries/{id}` - Delete entry
- `GET /api/knowledge/stats` - Get statistics

**Example API Call**:
```bash
# Get all entries
curl https://web-production-fa001.up.railway.app/api/knowledge/entries

# Create new entry
curl -X POST https://web-production-fa001.up.railway.app/api/knowledge/entries \
  -H "Content-Type: application/json" \
  -d '{
    "category": "example_nudge",
    "title": "Price negotiation follow-up",
    "content": "Ravi, the Asian Polytech discount discussion — what was their final ask? Update by EOD.",
    "language": "hinglish_80",
    "priority": 8,
    "created_by": "Mukul"
  }'
```

### 3. ✅ AI Brain Integration
The AI now automatically uses knowledge base entries when generating nudges:
- Pulls top 10 most relevant entries based on language and priority
- Organizes by category (examples, products, terminology, guidelines)
- Injects into AI prompt for personalized responses

### 4. ✅ Sample Data Inserted
8 sample entries added:
- 2 example nudges (hinglish_80)
- 2 product info entries (Rust-X, Dr Bio)
- 2 terminology entries (LTV, at-risk customer)
- 2 guidelines (deadline format, tone for high-intensity reps)

### 5. ✅ CRM Sync Timing
**Current Setting**: Auto-sync every **60 minutes** (1 hour)
- Configured in: `app/config.py` → `CRM_POLL_INTERVAL_MINUTES = 60`
- Can be changed via environment variable: `CRM_POLL_INTERVAL_MINUTES`

### 6. ✅ Indian Standard Time (IST) Support
**Utility Module Created**: `app/utils/timezone.py`

Functions available:
- `utc_to_ist(dt)` - Convert UTC to IST
- `ist_to_utc(dt)` - Convert IST to UTC
- `now_ist()` - Get current IST time
- `format_ist(dt)` - Format datetime in IST
- `format_ist_time(dt)` - Format time only (HH:MM)
- `format_ist_date(dt)` - Format date only (DD-MM-YYYY)

**Usage Example**:
```python
from app.utils.timezone import utc_to_ist, format_ist_datetime

# Convert database UTC time to IST for display
ist_time = utc_to_ist(conversation.created_at)
display_time = format_ist_datetime(ist_time)  # "02-05-2026 13:30"
```

---

## How to Use the Knowledge Base:

### Option 1: Via API (Postman/curl)
Use the API endpoints above to manage entries programmatically.

### Option 2: Via Frontend UI (Coming Next)
A simple web interface will be added to manage knowledge entries visually.

### Option 3: Direct Database
Connect to Railway PostgreSQL and insert/update entries directly.

---

## Knowledge Base Categories:

### 1. **example_nudge**
Real examples of good nudges that AI should learn from.
- Use actual messages that worked well
- Include different scenarios (follow-up, cross-sell, escalation)
- Specify language (hinglish_80, english_only, etc.)

### 2. **product_info**
Product knowledge, features, use cases, target customers.
- Product lines (Rust-X, Dr Bio, Tuffpaulin, KIF, EVA)
- Technical specs
- Target industries
- Cross-sell opportunities

### 3. **terminology**
Company-specific terms, abbreviations, internal jargon.
- LTV, at-risk, dormant, key account
- CRM codes, emp codes
- Regional terms

### 4. **guideline**
Communication rules and best practices.
- Deadline formats
- Tone guidelines per rep intensity
- What to avoid
- Escalation triggers

---

## How AI Uses Knowledge Base:

When generating a nudge, the AI:
1. Fetches top 10 entries matching the rep's language
2. Groups by category
3. Injects into prompt as additional context
4. AI learns patterns from examples
5. Applies product knowledge and terminology
6. Follows guidelines

**Result**: More personalized, accurate, company-specific nudges!

---

## Next Steps:

### To Add More Knowledge:
```bash
# Example: Add product knowledge
curl -X POST https://web-production-fa001.up.railway.app/api/knowledge/entries \
  -H "Content-Type: application/json" \
  -d '{
    "category": "product_info",
    "title": "Tuffpaulin GSM Variants",
    "content": "Tuffpaulin available in 250GSM, 300GSM, 350GSM. Higher GSM = more durability. 250GSM for light duty, 300GSM standard, 350GSM heavy industrial.",
    "language": "all",
    "priority": 8,
    "created_by": "Mukul"
  }'
```

### To Update CRM Sync Timing:
1. Go to Railway dashboard
2. Click web service → Variables
3. Update `CRM_POLL_INTERVAL_MINUTES` (e.g., 30 for 30 minutes, 120 for 2 hours)
4. Redeploy

### To Use IST in Frontend:
```javascript
// In frontend JavaScript
const utcTime = "2026-05-02T07:30:00Z";
const istTime = new Date(utcTime).toLocaleString('en-IN', {
  timeZone: 'Asia/Kolkata',
  hour12: false,
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit'
});
// Output: "02/05/2026, 13:00" (IST)
```

---

## Files Created:

1. `app/models.py` - Added AIKnowledgeBase model
2. `app/api/knowledge_base.py` - API endpoints
3. `app/services/ai_brain.py` - Updated to use knowledge base
4. `app/utils/timezone.py` - IST timezone utilities
5. `add_knowledge_base_table.py` - Migration script (completed)
6. `AI_KNOWLEDGE_BASE_SETUP.md` - This documentation

---

## Summary:

✅ **AI Knowledge Base**: Database table + API ready  
✅ **AI Integration**: Nudges now use knowledge base  
✅ **CRM Sync**: Every 60 minutes (configurable)  
✅ **IST Support**: Timezone utilities ready  
✅ **Sample Data**: 8 entries added  

**Your AI is now trainable and will generate more personalized nudges based on your knowledge base!**

Test it: https://web-production-fa001.up.railway.app/api/knowledge/entries

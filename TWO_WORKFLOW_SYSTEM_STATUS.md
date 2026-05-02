# Two-Workflow System Status Report

## Current Database State ✅

**Total Conversations: 25,540**

### Breakdown by Source:
1. **Check-in Conversations: 4,299** (Sales reps only)
   - `visit_completed`: 750 (check-ins WITH comments)
   - `visit_pending_comment`: 3,549 (check-ins WITHOUT comments - HIGH PRIORITY)

2. **Comment-based Conversations: 21,241** (ALL rep types)
   - Sales: 5,858
   - CCare: 4,704
   - NewBiz: 7,712
   - Finance: 2,961
   - Admin: 1

### Total by Rep Type:
- **Sales**: 10,157 (4,299 check-ins + 5,858 comments)
- **CCare**: 4,704 (comments only)
- **NewBiz**: 7,712 (comments only)
- **Finance**: 2,961 (comments only)
- **Admin**: 1 (comments only)

---

## Two Distinct Workflows

### Workflow 1: CCare & NewBiz (Back Office) 📞
**Rep Types**: `ccare`, `newbiz`

**Characteristics**:
- Sit in office
- Make calls to clients
- Add comments in CRM about business conversations
- **NO check-ins** (no field visits)

**AI Behavior**:
- Analyzes CRM comments only
- Generates nudges based on comment content
- Asks follow-up questions if needed

**Inbox Display**:
- Show comment-based conversations
- Badge: "CRM Comment" or "Office Call"
- Filter: CCare / NewBiz

---

### Workflow 2: Sales (Field Sales) 🚗
**Rep Type**: `sales`

**Characteristics**:
- Visit customer locations
- Check-in/check-out at each visit
- Sometimes add comments with check-ins, sometimes don't

**Two Sub-scenarios**:

#### A. Visit WITH Comment (750 conversations)
- Rep visits customer → check-in recorded
- Rep adds comment about the visit
- AI analyzes BOTH check-in data AND comment together
- Pipeline stage: `visit_completed`
- Urgency: MEDIUM
- Badge: "Visit + Comment"

#### B. Visit WITHOUT Comment (3,549 conversations)
- Rep visits customer → check-in recorded
- Rep does NOT add comment
- AI asks: "What happened in this visit?"
- Pipeline stage: `visit_pending_comment`
- Urgency: HIGH (needs immediate follow-up)
- Badge: "Visit - No Comment"

#### C. CRM Comments (5,858 conversations)
- Sales reps also add regular CRM comments (not linked to visits)
- AI analyzes comments like CCare/NewBiz workflow
- Pipeline stage: `Field visit follow-up`
- Badge: "CRM Comment"

**Inbox Display**:
- Show ALL three types of conversations
- Filters:
  - "Check-in Visits" (A + B)
  - "CRM Comments" (C)
  - "Needs Comment" (B only - high priority)

---

## Database Schema ✅

### Conversations Table
- `crm_ref`: 
  - `"checkin_{id}"` = Check-in conversation
  - Other values = Comment-based conversation
- `pipeline_stage`:
  - `visit_completed` = Check-in WITH comment
  - `visit_pending_comment` = Check-in WITHOUT comment
  - `Field visit follow-up` = Comment-based

### Reps Table
- `rep_type`: `sales`, `ccare`, `newbiz`, `admin`, `finance`

### CheckIns Table
- `comment_id`: Links check-in to CRM comment (if exists)
- 750 check-ins have linked comments
- 4,828 check-ins don't have comments

---

## API Updates ✅

### `/api/conversations` Endpoint
**New Query Parameters**:
- `rep_type`: Filter by `sales`, `ccare`, `newbiz`, etc.
- `source`: Filter by `checkin` (visits) or `comment` (CRM comments)
- `handler`: Existing filter for AI/escalated/etc.

**Examples**:
```
GET /api/conversations?rep_type=sales&source=checkin
  → Returns all check-in conversations for sales reps

GET /api/conversations?rep_type=ccare
  → Returns all CCare conversations (comments only)

GET /api/conversations?rep_type=sales&source=comment
  → Returns comment-based conversations for sales reps

GET /api/conversations?source=checkin&pipeline_stage=visit_pending_comment
  → Returns high-priority visits without comments
```

---

## Frontend Updates Needed 🔧

### 1. Inbox Filters (Sidebar)
Add filter chips for:
- **Rep Type**: All / Sales / CCare / NewBiz
- **Source**: All / Check-in Visits / CRM Comments
- **Priority**: All / Needs Comment (high priority)

### 2. Conversation Badges
Add visual badges to distinguish:
- 🚗 **Visit + Comment** (green) - Sales check-in with comment
- ⚠️ **Visit - No Comment** (red) - Sales check-in without comment (HIGH PRIORITY)
- 💬 **CRM Comment** (blue) - Comment-based conversation
- 📞 **Office Call** (purple) - CCare/NewBiz comment

### 3. Conversation List Item
Update to show:
- Rep name + rep type badge (Sales/CCare/NewBiz)
- Customer name
- Conversation source badge
- Urgency indicator
- Last message preview

### 4. Chat Pane Header
Show conversation metadata:
- Rep type
- Conversation source (Check-in vs Comment)
- If check-in: Show visit date, time, location
- If linked comment exists: Show link to view both

---

## AI Nudge Generation Logic

### For CCare/NewBiz:
```python
# Analyze comment only
context = crm_comment.raw_text
nudge = ai_brain.generate_nudge(context, rep_type="ccare")
```

### For Sales - Visit WITH Comment:
```python
# Analyze BOTH check-in and comment
context = f"""
Visit Details:
- Date: {checkin.checkin_date}
- Time: {checkin.checkin_time}
- Location: {checkin.address}
- Customer: {customer.name}

Comment: {crm_comment.raw_text}
"""
nudge = ai_brain.generate_nudge(context, rep_type="sales")
```

### For Sales - Visit WITHOUT Comment:
```python
# Ask for visit details
nudge = f"Hi {rep.name}, I noticed you visited {customer.name} on {checkin.checkin_date}. Could you share what was discussed during this visit?"
```

---

## Next Steps

1. ✅ **Database**: All data exists correctly
2. ✅ **API**: Filters added to conversations endpoint
3. 🔧 **Frontend**: Update inbox UI with filters and badges
4. 🔧 **AI Logic**: Update nudge generation to handle both workflows
5. 🔧 **Testing**: Verify filtering works correctly

---

## Key Insights

1. **Sales reps have BOTH workflows**: They do field visits (check-ins) AND add regular CRM comments
2. **CCare/NewBiz have ONE workflow**: Comments only, no check-ins
3. **High Priority**: 3,549 sales visits without comments need immediate follow-up
4. **Data Integrity**: All 25,540 conversations are properly categorized and linked

---

## User's Original Request Summary

> "We have two scenarios:
> 1. CCARE and NEWBIZ staff sit in back office, do client calling, put comments, no check-in/checkout. AI analyzes comments and generates nudges.
> 2. Sales team visits client locations, have check-ins. Sometimes they put comments with visits, sometimes they don't. In case of sales reps, we analyze BOTH comments and check-ins. If comments are not there, AI will generate nudges asking 'What happened in this visit?'"

**Status**: ✅ Database structure supports this perfectly. Frontend needs updates to visualize it properly.

# Rep Dashboard Implementation - Complete

## ✅ What's Been Done

### 1. Database Schema Updates

#### Added `rep_type` field to `reps` table
- **Values**: `sales`, `ccare`, `newbiz`, `admin`, `finance`
- **Distribution**:
  - Sales: 58 reps
  - CCare: 13 reps
  - NewBiz: 18 reps
  - Admin: 1 rep
  - Finance: 6 reps

#### Added `comment_id` field to `checkins` table
- Links check-ins to CRM comments
- **750 check-ins linked** to comments (13.4% link rate)
- Allows tracking which visits have associated comments

### 2. Data Linking Strategy

**Check-in to Comment Linking:**
- Matches based on: `emp_code`, `comp_code`, and `date`
- Handles different date formats:
  - Check-ins: `DD-MM-YYYY`
  - Comments: `MM/DD/YYYY HH:MM:SS`
- Successfully linked 750 visits to their comments

**Example Linked Data:**
```
Rep: Anil Gore (1755)
Customer: Krushna Tarpaulin stores
Check-in: 20-04-2026 at 11:41:05
Comment: "visit done order follow up done..."
```

### 3. API Endpoints Created

#### `/api/rep-dashboard/rep/{emp_code}`
Get dashboard data for a specific rep based on their type.

**For Sales Reps:**
```json
{
  "rep": {
    "emp_code": "1755",
    "name": "Anil Gore",
    "role": "SALES PERSON",
    "rep_type": "sales"
  },
  "data": {
    "type": "sales",
    "summary": {
      "total_visits": 45,
      "unique_customers": 23,
      "visits_with_comments": 15,
      "visits_without_comments": 30,
      "avg_visits_per_day": 6.4
    },
    "visits_by_date": {
      "28-04-2026": [
        {
          "customer": "Milan Hardware",
          "checkin_time": "10:48:16",
          "has_comment": true,
          "comment_id": 1234
        }
      ]
    },
    "needs_followup": [
      {
        "customer": "ABC Company",
        "date": "29-04-2026",
        "reason": "No comment added after visit"
      }
    ]
  }
}
```

**For CCare/NewBiz Reps:**
```json
{
  "rep": {
    "emp_code": "1744",
    "name": "Manpreet Kaur Walia",
    "role": "CCARE",
    "rep_type": "ccare"
  },
  "data": {
    "type": "comment_based",
    "summary": {
      "total_comments": 120,
      "pending": 15,
      "resolved": 95,
      "escalated": 10,
      "total_conversations": 45,
      "fresh_conversations": 8
    },
    "comments_by_status": {
      "pending": [...],
      "resolved": [...],
      "escalated": [...]
    },
    "ai_nudges": [
      {
        "id": "conv_123",
        "customer": "XYZ Corp",
        "topic": "Follow up on order",
        "urgency": "high",
        "confidence": 85
      }
    ]
  }
}
```

#### `/api/rep-dashboard/team/overview`
Get team overview with breakdown by rep type.

```bash
GET /api/rep-dashboard/team/overview?rep_type=sales&days=7
```

**Response:**
```json
{
  "period": {
    "days": 7,
    "from_date": "23-04-2026",
    "to_date": "30-04-2026"
  },
  "summary": {
    "total_reps": 58,
    "total_checkins": 1234,
    "total_comments": 9304,
    "total_conversations": 9309
  },
  "reps_by_type": {
    "sales": [
      {"emp_code": "1755", "name": "Anil Gore", "role": "SALES PERSON"},
      ...
    ],
    "ccare": [...],
    "newbiz": [...]
  },
  "type_counts": {
    "sales": 58,
    "ccare": 13,
    "newbiz": 18
  }
}
```

#### `/api/rep-dashboard/checkin/{checkin_id}/comment`
Get the comment associated with a specific check-in.

```bash
GET /api/rep-dashboard/checkin/5457/comment
```

**Response:**
```json
{
  "checkin": {
    "id": 5457,
    "customer": "Krushna Tarpaulin stores",
    "date": "20-04-2026",
    "time": "11:41:05",
    "address": "Pune, Maharashtra"
  },
  "comment": {
    "id": 1234,
    "text": "visit done order follow up done",
    "date": "04/20/2026 11:45:00",
    "status": "resolved",
    "followup_question": "What was the order value?",
    "rep_reply": "Order worth 50k placed",
    "confidence_score": 85
  }
}
```

---

## 🎯 How It Works

### For Sales Reps (Field Sales)
1. **Check-ins tracked**: Every visit to a customer location
2. **Visit analysis**: Which visits have comments, which don't
3. **Follow-up alerts**: Visits without comments need follow-up
4. **AI can ask**: "You visited ABC Company today. What was discussed?"

### For CCare Reps (Customer Care)
1. **Comment-based workflow**: AI processes CRM comments
2. **AI nudges**: Generated based on customer comments
3. **Conversation tracking**: All customer interactions
4. **No check-ins**: They work from office, not field visits

### For NewBiz Reps (New Business)
1. **Similar to CCare**: Comment and conversation focused
2. **Lead tracking**: New customer acquisition
3. **AI assistance**: Follow-up questions on new leads
4. **No check-ins**: Office-based work

---

## 🚀 Next Steps: Frontend Dashboard

### Recommended Frontend Structure

#### 1. Team View (Main Dashboard)
```
┌─────────────────────────────────────────────┐
│  Hi-Tech Sales Team Dashboard               │
├─────────────────────────────────────────────┤
│  Filter: [All] [Sales] [CCare] [NewBiz]    │
├─────────────────────────────────────────────┤
│                                              │
│  📊 Summary (Last 7 Days)                   │
│  ├─ Total Reps: 96                          │
│  ├─ Check-ins: 1,234 (Sales)                │
│  ├─ Comments: 9,304                          │
│  └─ Conversations: 9,309                     │
│                                              │
│  👥 Sales Reps (58)                          │
│  ┌──────────────────────────────────┐       │
│  │ Anil Gore (1755)                 │       │
│  │ ├─ 45 visits this week           │       │
│  │ ├─ 23 unique customers           │       │
│  │ └─ ⚠️  30 visits need comments   │       │
│  └──────────────────────────────────┘       │
│                                              │
│  💬 CCare Reps (13)                          │
│  ┌──────────────────────────────────┐       │
│  │ Manpreet Kaur Walia (1744)       │       │
│  │ ├─ 120 comments processed        │       │
│  │ ├─ 15 pending                    │       │
│  │ └─ 8 AI nudges sent              │       │
│  └──────────────────────────────────┘       │
│                                              │
└─────────────────────────────────────────────┘
```

#### 2. Sales Rep Individual View
```
┌─────────────────────────────────────────────┐
│  Anil Gore (1755) - Sales Rep               │
├─────────────────────────────────────────────┤
│  📊 This Week                                │
│  ├─ 45 visits                                │
│  ├─ 23 customers                             │
│  ├─ 15 with comments ✅                      │
│  └─ 30 need follow-up ⚠️                     │
├─────────────────────────────────────────────┤
│  📅 Visits by Date                           │
│                                              │
│  28-04-2026 (Monday)                         │
│  ┌──────────────────────────────────┐       │
│  │ 10:48 - Milan Hardware           │       │
│  │ ✅ Comment: "visit done..."      │       │
│  │ [View Details] [Ask AI]          │       │
│  └──────────────────────────────────┘       │
│  ┌──────────────────────────────────┐       │
│  │ 11:11 - Kand patil traders       │       │
│  │ ✅ Comment: "order follow up..." │       │
│  │ [View Details]                   │       │
│  └──────────────────────────────────┘       │
│                                              │
│  29-04-2026 (Tuesday)                        │
│  ┌──────────────────────────────────┐       │
│  │ 09:30 - ABC Company              │       │
│  │ ⚠️  No comment added             │       │
│  │ [Ask Rep: What happened?]        │       │
│  └──────────────────────────────────┘       │
│                                              │
└─────────────────────────────────────────────┘
```

#### 3. CCare/NewBiz Rep Individual View
```
┌─────────────────────────────────────────────┐
│  Manpreet Kaur Walia (1744) - CCare         │
├─────────────────────────────────────────────┤
│  📊 This Week                                │
│  ├─ 120 comments                             │
│  ├─ 15 pending                               │
│  ├─ 95 resolved                              │
│  └─ 8 AI nudges sent                         │
├─────────────────────────────────────────────┤
│  🤖 AI Nudges                                │
│                                              │
│  ┌──────────────────────────────────┐       │
│  │ XYZ Corp - Follow up on order    │       │
│  │ Urgency: High | Confidence: 85%  │       │
│  │ [View Conversation]              │       │
│  └──────────────────────────────────┘       │
│                                              │
│  ⏳ Pending Comments                         │
│                                              │
│  ┌──────────────────────────────────┐       │
│  │ ABC Industries                   │       │
│  │ "Customer asking about pricing"  │       │
│  │ AI Question: "What price quoted?"│       │
│  │ [Reply] [Escalate]               │       │
│  └──────────────────────────────────┘       │
│                                              │
└─────────────────────────────────────────────┘
```

---

## 🔧 Frontend Implementation Guide

### Step 1: Add Rep Dashboard Tab

In `frontend/index.html`, add a new tab:

```html
<div class="tab" data-tab="rep-dashboard">
  <i class="icon">👥</i>
  <span>Team</span>
</div>
```

### Step 2: Create Dashboard Container

```html
<div id="rep-dashboard-view" class="view-container" style="display:none;">
  <div class="dashboard-header">
    <h2>Team Dashboard</h2>
    <div class="filter-buttons">
      <button class="filter-btn active" data-type="all">All</button>
      <button class="filter-btn" data-type="sales">Sales</button>
      <button class="filter-btn" data-type="ccare">CCare</button>
      <button class="filter-btn" data-type="newbiz">NewBiz</button>
    </div>
  </div>
  
  <div id="team-summary" class="summary-cards">
    <!-- Summary cards will be loaded here -->
  </div>
  
  <div id="reps-list" class="reps-grid">
    <!-- Rep cards will be loaded here -->
  </div>
</div>
```

### Step 3: JavaScript Functions

```javascript
// Load team overview
async function loadTeamDashboard(repType = null) {
  const url = repType 
    ? `/api/rep-dashboard/team/overview?rep_type=${repType}&days=7`
    : `/api/rep-dashboard/team/overview?days=7`;
  
  const response = await fetch(url);
  const data = await response.json();
  
  // Display summary
  document.getElementById('team-summary').innerHTML = `
    <div class="summary-card">
      <h3>${data.summary.total_reps}</h3>
      <p>Total Reps</p>
    </div>
    <div class="summary-card">
      <h3>${data.summary.total_checkins}</h3>
      <p>Check-ins</p>
    </div>
    <div class="summary-card">
      <h3>${data.summary.total_comments}</h3>
      <p>Comments</p>
    </div>
    <div class="summary-card">
      <h3>${data.summary.total_conversations}</h3>
      <p>Conversations</p>
    </div>
  `;
  
  // Display reps by type
  let repsHTML = '';
  for (const [type, reps] of Object.entries(data.reps_by_type)) {
    repsHTML += `<h3>${type.toUpperCase()} (${reps.length})</h3>`;
    repsHTML += '<div class="reps-grid">';
    for (const rep of reps) {
      repsHTML += `
        <div class="rep-card" onclick="loadRepDashboard('${rep.emp_code}')">
          <div class="rep-avatar">${rep.name.substring(0, 2)}</div>
          <div class="rep-info">
            <h4>${rep.name}</h4>
            <p>${rep.role}</p>
            <p class="rep-region">${rep.region}</p>
          </div>
        </div>
      `;
    }
    repsHTML += '</div>';
  }
  document.getElementById('reps-list').innerHTML = repsHTML;
}

// Load individual rep dashboard
async function loadRepDashboard(empCode) {
  const response = await fetch(`/api/rep-dashboard/rep/${empCode}?days=7`);
  const data = await response.json();
  
  if (data.rep.rep_type === 'sales') {
    displaySalesRepDashboard(data);
  } else {
    displayCommentBasedRepDashboard(data);
  }
}

// Display sales rep dashboard
function displaySalesRepDashboard(data) {
  const rep = data.rep;
  const summary = data.data.summary;
  
  let html = `
    <div class="rep-dashboard">
      <div class="rep-header">
        <h2>${rep.name} (${rep.emp_code})</h2>
        <p>${rep.role} - ${rep.region}</p>
      </div>
      
      <div class="summary-cards">
        <div class="card">
          <h3>${summary.total_visits}</h3>
          <p>Total Visits</p>
        </div>
        <div class="card">
          <h3>${summary.unique_customers}</h3>
          <p>Unique Customers</p>
        </div>
        <div class="card ${summary.visits_without_comments > 0 ? 'warning' : ''}">
          <h3>${summary.visits_without_comments}</h3>
          <p>Need Follow-up</p>
        </div>
      </div>
      
      <h3>Visits by Date</h3>
      <div class="visits-timeline">
  `;
  
  for (const [date, visits] of Object.entries(data.data.visits_by_date)) {
    html += `<div class="date-group"><h4>${date}</h4>`;
    for (const visit of visits) {
      html += `
        <div class="visit-card ${visit.has_comment ? 'has-comment' : 'needs-comment'}">
          <div class="visit-time">${visit.checkin_time}</div>
          <div class="visit-customer">${visit.customer}</div>
          ${visit.has_comment 
            ? '<span class="badge success">✅ Comment</span>' 
            : '<span class="badge warning">⚠️ No Comment</span>'}
          <button onclick="viewCheckinDetails(${visit.id})">Details</button>
        </div>
      `;
    }
    html += '</div>';
  }
  
  html += '</div></div>';
  
  // Display in modal or dedicated view
  document.getElementById('rep-detail-view').innerHTML = html;
  document.getElementById('rep-detail-view').style.display = 'block';
}

// Display CCare/NewBiz rep dashboard
function displayCommentBasedRepDashboard(data) {
  const rep = data.rep;
  const summary = data.data.summary;
  
  let html = `
    <div class="rep-dashboard">
      <div class="rep-header">
        <h2>${rep.name} (${rep.emp_code})</h2>
        <p>${rep.role} - ${rep.region}</p>
      </div>
      
      <div class="summary-cards">
        <div class="card">
          <h3>${summary.total_comments}</h3>
          <p>Total Comments</p>
        </div>
        <div class="card ${summary.pending > 0 ? 'warning' : ''}">
          <h3>${summary.pending}</h3>
          <p>Pending</p>
        </div>
        <div class="card">
          <h3>${summary.resolved}</h3>
          <p>Resolved</p>
        </div>
      </div>
      
      <h3>AI Nudges</h3>
      <div class="ai-nudges">
  `;
  
  for (const nudge of data.data.ai_nudges) {
    html += `
      <div class="nudge-card urgency-${nudge.urgency}">
        <h4>${nudge.customer}</h4>
        <p>${nudge.topic}</p>
        <div class="nudge-meta">
          <span class="badge ${nudge.urgency}">${nudge.urgency}</span>
          <span class="confidence">${nudge.confidence}% confidence</span>
        </div>
        <button onclick="viewConversation('${nudge.id}')">View</button>
      </div>
    `;
  }
  
  html += '</div></div>';
  
  document.getElementById('rep-detail-view').innerHTML = html;
  document.getElementById('rep-detail-view').style.display = 'block';
}

// View check-in details with comment
async function viewCheckinDetails(checkinId) {
  const response = await fetch(`/api/rep-dashboard/checkin/${checkinId}/comment`);
  const data = await response.json();
  
  // Display in modal
  showModal(`
    <h3>Visit Details</h3>
    <p><strong>Customer:</strong> ${data.checkin.customer}</p>
    <p><strong>Date:</strong> ${data.checkin.date} at ${data.checkin.time}</p>
    <p><strong>Address:</strong> ${data.checkin.address}</p>
    
    ${data.comment ? `
      <h4>Comment</h4>
      <p>${data.comment.text}</p>
      <p><strong>Status:</strong> ${data.comment.status}</p>
      ${data.comment.followup_question ? `
        <p><strong>AI Question:</strong> ${data.comment.followup_question}</p>
        <p><strong>Rep Reply:</strong> ${data.comment.rep_reply || 'Pending'}</p>
      ` : ''}
    ` : `
      <p class="warning">⚠️ No comment added for this visit</p>
      <button onclick="askRepAboutVisit(${checkinId})">Ask Rep</button>
    `}
  `);
}
```

### Step 4: CSS Styling

```css
.rep-dashboard {
  padding: 20px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.summary-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.summary-card.warning {
  border-left: 4px solid #ff9500;
}

.reps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.rep-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}

.rep-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.visit-card {
  background: white;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  border-left: 4px solid #34c759;
}

.visit-card.needs-comment {
  border-left-color: #ff9500;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.badge.success {
  background: #34c759;
  color: white;
}

.badge.warning {
  background: #ff9500;
  color: white;
}

.badge.high {
  background: #ff3b30;
  color: white;
}
```

---

## 📝 Summary

### ✅ Completed:
1. Added `rep_type` field to distinguish Sales/CCare/NewBiz reps
2. Added `comment_id` to link check-ins with comments
3. Linked 750 check-ins to their comments
4. Created comprehensive API endpoints for rep dashboards
5. Different data views for different rep types

### 🎯 Ready to Use:
- API endpoints are live and tested
- Data is properly linked
- Rep types are categorized

### 🚀 Next: Frontend
- Add Team Dashboard tab
- Create rep cards with type-specific views
- Show visits with/without comments for Sales reps
- Show AI nudges and pending comments for CCare/NewBiz reps
- Add "Ask Rep" functionality for visits without comments

---

## 🧪 Test the API

```bash
# Get team overview
curl "http://localhost:8002/api/rep-dashboard/team/overview?days=7"

# Get sales rep dashboard
curl "http://localhost:8002/api/rep-dashboard/rep/1755?days=7"

# Get CCare rep dashboard
curl "http://localhost:8002/api/rep-dashboard/rep/1744?days=7"

# Get check-in with comment
curl "http://localhost:8002/api/rep-dashboard/checkin/5457/comment"

# Filter by rep type
curl "http://localhost:8002/api/rep-dashboard/team/overview?rep_type=sales&days=7"
```

---

**Everything is ready! The backend is complete. Now you can build the frontend dashboard using the API endpoints provided.** 🎉

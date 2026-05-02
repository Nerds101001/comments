# Frontend Implementation Guide
## Two-Workflow System: Sales vs CCare/NewBiz

---

## Overview

The system now supports two distinct workflows:
1. **CCare/NewBiz**: Office-based, comments only, no check-ins
2. **Sales**: Field-based, check-ins + comments, both analyzed together

The frontend needs to visualize these workflows clearly with proper filters and badges.

---

## Required Frontend Changes

### 1. Add Filter Chips in Sidebar

**Location**: `.sidebar-head` → `.filter-chips`

**Current Filters**:
- All
- Fresh
- Escalated
- Approval

**New Filters to Add**:

```html
<!-- Rep Type Filters -->
<div class="filter-section">
  <div class="filter-label">Rep Type</div>
  <div class="filter-chips">
    <button class="chip active" data-filter-type="rep_type" data-filter-value="">All</button>
    <button class="chip" data-filter-type="rep_type" data-filter-value="sales">Sales</button>
    <button class="chip" data-filter-type="rep_type" data-filter-value="ccare">CCare</button>
    <button class="chip" data-filter-type="rep_type" data-filter-value="newbiz">NewBiz</button>
  </div>
</div>

<!-- Source Filters -->
<div class="filter-section">
  <div class="filter-label">Source</div>
  <div class="filter-chips">
    <button class="chip active" data-filter-type="source" data-filter-value="">All</button>
    <button class="chip" data-filter-type="source" data-filter-value="checkin">
      🚗 Check-in Visits
    </button>
    <button class="chip" data-filter-type="source" data-filter-value="comment">
      💬 CRM Comments
    </button>
  </div>
</div>

<!-- Priority Filter -->
<div class="filter-section">
  <div class="filter-label">Priority</div>
  <div class="filter-chips">
    <button class="chip" data-filter-type="priority" data-filter-value="high">
      ⚠️ Needs Comment (3,549)
    </button>
  </div>
</div>
```

**CSS for Filter Sections**:
```css
.filter-section {
  margin-bottom: 12px;
}
.filter-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-3);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 6px;
  padding: 0 4px;
}
```

---

### 2. Add Conversation Type Badges

**Location**: `.conv-item` → `.conv-badges`

**Badge Types**:

```javascript
function getConversationBadge(conv) {
  const isCheckin = conv.crm_ref && conv.crm_ref.startsWith('checkin_');
  const repType = conv.rep.rep_type;
  
  if (isCheckin) {
    // Check-in conversation (Sales only)
    if (conv.pipeline_stage === 'visit_pending_comment') {
      return {
        text: 'Visit - No Comment',
        class: 'badge-visit-pending',
        icon: '⚠️',
        color: 'red'
      };
    } else if (conv.pipeline_stage === 'visit_completed') {
      return {
        text: 'Visit + Comment',
        class: 'badge-visit-complete',
        icon: '🚗',
        color: 'green'
      };
    }
  } else {
    // Comment-based conversation
    if (repType === 'sales') {
      return {
        text: 'CRM Comment',
        class: 'badge-comment',
        icon: '💬',
        color: 'blue'
      };
    } else if (repType === 'ccare') {
      return {
        text: 'Office Call',
        class: 'badge-ccare',
        icon: '📞',
        color: 'purple'
      };
    } else if (repType === 'newbiz') {
      return {
        text: 'New Business',
        class: 'badge-newbiz',
        icon: '🎯',
        color: 'orange'
      };
    }
  }
  
  return {
    text: 'Comment',
    class: 'badge-default',
    icon: '💬',
    color: 'gray'
  };
}
```

**Badge HTML**:
```html
<div class="conv-badges">
  <span class="badge badge-visit-pending">⚠️ Visit - No Comment</span>
  <span class="pill urgency-high">High</span>
</div>
```

**Badge CSS**:
```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
  letter-spacing: -0.01em;
  white-space: nowrap;
}

.badge-visit-pending {
  background: var(--red-soft);
  color: var(--red);
}

.badge-visit-complete {
  background: var(--green-soft);
  color: var(--green);
}

.badge-comment {
  background: var(--blue-soft);
  color: var(--blue);
}

.badge-ccare {
  background: var(--purple-soft);
  color: var(--purple);
}

.badge-newbiz {
  background: var(--orange-soft);
  color: var(--orange);
}

.badge-default {
  background: var(--bg);
  color: var(--text-2);
}
```

---

### 3. Update Conversation List Item

**Enhanced Conv Item**:
```html
<div class="conv-item" data-conv-id="${conv.id}">
  <!-- Avatar -->
  <div class="rep-avatar" style="background: ${conv.rep.color}">
    ${conv.rep.avatar}
  </div>
  
  <!-- Info -->
  <div class="conv-info">
    <div class="conv-line1">
      <span class="conv-rep-name">
        ${conv.rep.name}
        <span class="rep-type-tag">${conv.rep.rep_type.toUpperCase()}</span>
      </span>
      <span class="conv-time">${formatTime(conv.updated_at)}</span>
    </div>
    
    <div class="conv-customer">
      ${conv.customer ? conv.customer.name : 'Unknown Customer'}
    </div>
    
    <div class="conv-preview ${conv.is_fresh ? 'unread' : ''}">
      ${getLastMessagePreview(conv)}
    </div>
  </div>
  
  <!-- Badges -->
  <div class="conv-badges">
    ${renderConversationBadge(conv)}
    ${renderUrgencyPill(conv)}
  </div>
</div>
```

**Rep Type Tag CSS**:
```css
.rep-type-tag {
  font-size: 8px;
  font-weight: 700;
  padding: 2px 5px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.08);
  color: var(--text-3);
  margin-left: 4px;
  letter-spacing: 0.04em;
}
```

---

### 4. Update Chat Pane Header

**Show Conversation Context**:
```html
<div class="chat-head">
  <div class="rep-avatar" style="background: ${conv.rep.color}">
    ${conv.rep.avatar}
  </div>
  
  <div>
    <div class="chat-rep-name">
      ${conv.rep.name}
      <span class="rep-type-tag">${conv.rep.rep_type.toUpperCase()}</span>
    </div>
    <div class="chat-rep-meta">
      ${conv.customer ? conv.customer.name : 'Unknown'} 
      <span>·</span> 
      ${getConversationTypeLabel(conv)}
    </div>
  </div>
  
  <div class="chat-actions">
    ${renderChatActions(conv)}
  </div>
</div>

<!-- If check-in, show visit details -->
${conv.crm_ref && conv.crm_ref.startsWith('checkin_') ? `
  <div class="visit-details-bar">
    <div class="visit-icon">🚗</div>
    <div class="visit-info">
      <strong>Visit Details:</strong>
      ${getCheckinDetails(conv)}
    </div>
    ${conv.has_linked_comment ? `
      <button class="btn-sm btn-tinted" onclick="viewLinkedComment('${conv.id}')">
        View Comment
      </button>
    ` : ''}
  </div>
` : ''}
```

**Visit Details Bar CSS**:
```css
.visit-details-bar {
  padding: 10px 22px;
  background: var(--blue-tint);
  border-bottom: 1px solid var(--separator);
  display: flex;
  align-items: center;
  gap: 12px;
}

.visit-icon {
  font-size: 20px;
}

.visit-info {
  flex: 1;
  font-size: 12px;
  color: var(--text-2);
  line-height: 1.5;
}

.visit-info strong {
  color: var(--text);
  font-weight: 600;
}
```

---

### 5. Update API Calls

**Fetch Conversations with Filters**:
```javascript
async function fetchConversations(filters = {}) {
  const params = new URLSearchParams();
  
  if (filters.handler) params.append('handler', filters.handler);
  if (filters.rep_type) params.append('rep_type', filters.rep_type);
  if (filters.source) params.append('source', filters.source);
  if (filters.limit) params.append('limit', filters.limit);
  if (filters.offset) params.append('offset', filters.offset);
  
  const response = await fetch(`/api/conversations?${params}`);
  return await response.json();
}

// Example usage:
// All sales check-in conversations
const salesVisits = await fetchConversations({ 
  rep_type: 'sales', 
  source: 'checkin' 
});

// All CCare conversations
const ccareConvs = await fetchConversations({ 
  rep_type: 'ccare' 
});

// High priority visits without comments
const needsComment = await fetchConversations({ 
  source: 'checkin',
  // Then filter client-side for pipeline_stage === 'visit_pending_comment'
});
```

---

### 6. Filter Logic

**JavaScript Filter Handler**:
```javascript
let activeFilters = {
  handler: '',
  rep_type: '',
  source: '',
  priority: ''
};

function applyFilters() {
  const filters = {};
  
  if (activeFilters.handler) filters.handler = activeFilters.handler;
  if (activeFilters.rep_type) filters.rep_type = activeFilters.rep_type;
  if (activeFilters.source) filters.source = activeFilters.source;
  
  fetchConversations(filters).then(conversations => {
    // If priority filter is active, filter client-side
    let filtered = conversations;
    if (activeFilters.priority === 'high') {
      filtered = conversations.filter(c => 
        c.urgency === 'high' && 
        c.pipeline_stage === 'visit_pending_comment'
      );
    }
    
    renderConversationList(filtered);
  });
}

// Attach to filter chips
document.querySelectorAll('.chip[data-filter-type]').forEach(chip => {
  chip.addEventListener('click', (e) => {
    const filterType = e.target.dataset.filterType;
    const filterValue = e.target.dataset.filterValue;
    
    // Update active filters
    activeFilters[filterType] = filterValue;
    
    // Update UI
    e.target.parentElement.querySelectorAll('.chip').forEach(c => 
      c.classList.remove('active')
    );
    e.target.classList.add('active');
    
    // Apply filters
    applyFilters();
  });
});
```

---

### 7. Dashboard KPI Updates

**Add New KPIs**:
```html
<!-- Visits Without Comments -->
<div class="kpi-card" onclick="filterConversations('needs-comment')">
  <div class="kpi-head">
    <div class="kpi-icon red">⚠️</div>
    <div class="kpi-trend">HIGH</div>
  </div>
  <div class="kpi-value">3,549</div>
  <div class="kpi-label">Visits Need Comments</div>
</div>

<!-- Sales Check-ins -->
<div class="kpi-card" onclick="filterConversations('sales-visits')">
  <div class="kpi-head">
    <div class="kpi-icon blue">🚗</div>
    <div class="kpi-trend">SALES</div>
  </div>
  <div class="kpi-value">4,299</div>
  <div class="kpi-label">Field Visits</div>
</div>

<!-- CCare/NewBiz Comments -->
<div class="kpi-card" onclick="filterConversations('office-calls')">
  <div class="kpi-head">
    <div class="kpi-icon purple">📞</div>
    <div class="kpi-trend">OFFICE</div>
  </div>
  <div class="kpi-value">12,416</div>
  <div class="kpi-label">Office Calls</div>
</div>
```

---

## Implementation Checklist

- [ ] Add filter sections to sidebar
- [ ] Create badge components and CSS
- [ ] Update conversation list item template
- [ ] Add visit details bar to chat pane
- [ ] Implement filter logic in JavaScript
- [ ] Update API calls with new parameters
- [ ] Add dashboard KPIs
- [ ] Test all filter combinations
- [ ] Verify badge colors and icons
- [ ] Test with real data

---

## Testing Scenarios

### Test 1: Filter by Rep Type
1. Click "Sales" filter
2. Should show 10,157 conversations (4,299 check-ins + 5,858 comments)
3. Should see mix of visit and comment badges

### Test 2: Filter by Source
1. Click "Check-in Visits" filter
2. Should show 4,299 conversations (Sales only)
3. All should have visit badges (green or red)

### Test 3: High Priority Filter
1. Click "Needs Comment" filter
2. Should show 3,549 conversations
3. All should have red "Visit - No Comment" badge
4. All should have "High" urgency pill

### Test 4: Combined Filters
1. Select "Sales" + "CRM Comments"
2. Should show 5,858 conversations
3. All should have blue "CRM Comment" badge
4. No visit badges should appear

### Test 5: CCare Filter
1. Click "CCare" filter
2. Should show 4,704 conversations
3. All should have purple "Office Call" badge
4. No visit badges should appear

---

## API Endpoints Reference

```
GET /api/conversations
  ?rep_type=sales          # Filter by rep type
  &source=checkin          # Filter by source (checkin/comment)
  &handler=ai              # Filter by handler
  &limit=100               # Pagination
  &offset=0                # Pagination

GET /api/rep-dashboard/rep/{emp_code}
  ?days=7                  # Get rep-specific dashboard

GET /api/rep-dashboard/team/overview
  ?rep_type=sales          # Team overview by type
  &days=7

GET /api/checkin/{checkin_id}/comment
  # Get linked comment for a check-in
```

---

## Summary

The frontend now needs to:
1. **Visualize two workflows** clearly with filters and badges
2. **Show conversation source** (check-in vs comment)
3. **Highlight high priority** visits without comments
4. **Support filtering** by rep type, source, and priority
5. **Display visit details** for check-in conversations

All backend support is in place. The frontend just needs UI updates to expose these capabilities to users.

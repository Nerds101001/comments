# Frontend CRM Sync Feature - Implementation Guide

## Overview
This document outlines the changes needed to add CRM sync functionality to the frontend with:
1. Manual sync button in the topbar
2. CRM comments view showing all pending/processed comments
3. Real-time sync status display
4. Automatic background sync every 1 hour

## Backend Changes (COMPLETED ✅)

### 1. Updated `app/api/crm.py`
- ✅ Added incremental sync support (fetches only new comments since last sync)
- ✅ Added `/api/crm/sync-status` endpoint to get sync information
- ✅ Modified `/api/crm/sync` to track last sync time in database
- ✅ Returns sync metadata (new_comments, last_sync, hours_back)

### 2. Updated `.env`
- ✅ Changed `CRM_POLL_INTERVAL_MINUTES` from 30 to 60 (1 hour)

### 3. Updated `app/main.py`
- ✅ Background scheduler already configured to poll CRM every 60 minutes
- ✅ Auto-processes pending comments after sync

## Frontend Changes (TO BE IMPLEMENTED)

### 1. Add Sync Button to Topbar

**Location:** In the `<div class="topbar-right">` section

```html
<!-- Add this button before the settings button -->
<button class="btn btn-tinted-green btn-sm" id="syncCRMBtn" onclick="syncCRM()">
  <span id="syncIcon">↻</span>
  <span id="syncText">Sync CRM</span>
</button>
```

### 2. Add CRM Comments View

**Location:** Add a new view after the existing views

```html
<!-- CRM COMMENTS VIEW -->
<main class="view" id="viewCRM">
  <div class="crm-container">
    <div class="crm-header">
      <div>
        <h1>CRM Comments</h1>
        <p class="crm-subtitle">
          <span id="crmTotalCount">0</span> total comments · 
          <span id="crmPendingCount">0</span> pending · 
          <span id="crmProcessedCount">0</span> processed
        </p>
      </div>
      <div class="crm-actions">
        <button class="btn btn-secondary" onclick="syncCRM()">
          <span>↻</span> Sync Now
        </button>
        <button class="btn btn-primary" onclick="processAllPending()">
          Process All Pending
        </button>
      </div>
    </div>
    
    <div class="crm-sync-status" id="crmSyncStatus">
      <div class="sync-info">
        <span class="sync-label">Last Sync:</span>
        <span class="sync-value" id="lastSyncTime">Never</span>
      </div>
      <div class="sync-info">
        <span class="sync-label">Next Auto-Sync:</span>
        <span class="sync-value" id="nextSyncTime">--</span>
      </div>
    </div>
    
    <div class="crm-filters">
      <button class="chip active" data-filter="all" onclick="filterCRMComments('all')">All</button>
      <button class="chip" data-filter="pending" onclick="filterCRMComments('pending')">Pending</button>
      <button class="chip" data-filter="followup_sent" onclick="filterCRMComments('followup_sent')">Follow-up Sent</button>
      <button class="chip" data-filter="resolved" onclick="filterCRMComments('resolved')">Resolved</button>
      <button class="chip" data-filter="escalated" onclick="filterCRMComments('escalated')">Escalated</button>
    </div>
    
    <div class="crm-list" id="crmCommentsList">
      <!-- Comments will be loaded here -->
    </div>
  </div>
</main>
```

### 3. Add CRM Tab to Segmented Control

**Location:** In the `<div class="segmented">` section

```html
<button class="seg-btn" data-view="viewCRM" onclick="switchView('viewCRM')">
  <span>📋</span>
  CRM
  <span class="seg-badge" id="crmBadge">0</span>
</button>
```

### 4. Add CSS Styles

```css
/* CRM Container */
.crm-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 28px 24px 80px;
}

.crm-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.crm-header h1 {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.025em;
  line-height: 1.1;
  margin-bottom: 4px;
}

.crm-subtitle {
  font-size: 14px;
  color: var(--text-2);
  letter-spacing: -0.01em;
}

.crm-actions {
  display: flex;
  gap: 10px;
}

/* Sync Status Bar */
.crm-sync-status {
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 20px;
  display: flex;
  gap: 32px;
}

.sync-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sync-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.sync-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  font-family: var(--font-mono);
}

/* CRM Filters */
.crm-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

/* CRM Comment Card */
.crm-comment-card {
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 12px;
  transition: box-shadow 0.15s ease;
  cursor: pointer;
}

.crm-comment-card:hover {
  box-shadow: var(--shadow-md);
}

.crm-comment-card.pending {
  border-left: 3px solid var(--orange);
}

.crm-comment-card.followup_sent {
  border-left: 3px solid var(--blue);
}

.crm-comment-card.resolved {
  border-left: 3px solid var(--green);
}

.crm-comment-card.escalated {
  border-left: 3px solid var(--red);
}

.crm-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.crm-card-rep {
  display: flex;
  align-items: center;
  gap: 10px;
}

.crm-card-rep-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.crm-card-rep-info h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 2px;
}

.crm-card-rep-info p {
  font-size: 11px;
  color: var(--text-3);
}

.crm-card-meta {
  text-align: right;
}

.crm-card-date {
  font-size: 11px;
  color: var(--text-3);
  font-family: var(--font-mono);
}

.crm-card-body {
  margin-bottom: 12px;
}

.crm-card-text {
  font-size: 13px;
  color: var(--text);
  line-height: 1.5;
  background: var(--bg-2);
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 8px;
}

.crm-card-summary {
  font-size: 12px;
  color: var(--text-2);
  line-height: 1.5;
  font-style: italic;
}

.crm-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.crm-card-actions {
  display: flex;
  gap: 6px;
}

/* Sync button animation */
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.syncing {
  animation: rotate 1s linear infinite;
}
```

### 5. Add JavaScript Functions

```javascript
// Global state
let crmComments = [];
let currentFilter = 'all';
let syncInterval = null;

// Initialize CRM sync status on page load
async function initCRMSync() {
  await loadCRMSyncStatus();
  await loadCRMComments();
  
  // Set up auto-refresh every 30 seconds
  setInterval(loadCRMSyncStatus, 30000);
  
  // Calculate next sync time (every 60 minutes)
  updateNextSyncTime();
  setInterval(updateNextSyncTime, 60000);
}

// Load CRM sync status
async function loadCRMSyncStatus() {
  try {
    const res = await fetch('/api/crm/sync-status');
    const data = await res.json();
    
    if (data.status === 'ok') {
      const { last_sync, pending_count, processed_count, total_count } = data.data;
      
      // Update UI
      document.getElementById('crmTotalCount').textContent = total_count;
      document.getElementById('crmPendingCount').textContent = pending_count;
      document.getElementById('crmProcessedCount').textContent = processed_count;
      document.getElementById('crmBadge').textContent = pending_count;
      
      if (last_sync) {
        const lastSyncDate = new Date(last_sync);
        document.getElementById('lastSyncTime').textContent = formatRelativeTime(lastSyncDate);
      } else {
        document.getElementById('lastSyncTime').textContent = 'Never';
      }
    }
  } catch (error) {
    console.error('Failed to load CRM sync status:', error);
  }
}

// Manual CRM sync
async function syncCRM() {
  const btn = document.getElementById('syncCRMBtn');
  const icon = document.getElementById('syncIcon');
  const text = document.getElementById('syncText');
  
  // Disable button and show loading state
  btn.disabled = true;
  icon.classList.add('syncing');
  text.textContent = 'Syncing...';
  
  try {
    const res = await fetch('/api/crm/sync', { method: 'POST' });
    const data = await res.json();
    
    if (data.status === 'ok') {
      const { new_comments } = data.data;
      
      // Show success message
      text.textContent = `Synced ${new_comments} new`;
      
      // Reload data
      await loadCRMSyncStatus();
      await loadCRMComments();
      
      // Reset button after 2 seconds
      setTimeout(() => {
        text.textContent = 'Sync CRM';
        icon.classList.remove('syncing');
        btn.disabled = false;
      }, 2000);
    } else {
      throw new Error(data.message || 'Sync failed');
    }
  } catch (error) {
    console.error('CRM sync failed:', error);
    text.textContent = 'Sync Failed';
    icon.classList.remove('syncing');
    
    setTimeout(() => {
      text.textContent = 'Sync CRM';
      btn.disabled = false;
    }, 2000);
  }
}

// Load CRM comments
async function loadCRMComments(status = null) {
  try {
    const url = status ? `/api/crm/comments?status=${status}&limit=100` : '/api/crm/comments?limit=100';
    const res = await fetch(url);
    crmComments = await res.json();
    
    renderCRMComments();
  } catch (error) {
    console.error('Failed to load CRM comments:', error);
  }
}

// Filter CRM comments
function filterCRMComments(filter) {
  currentFilter = filter;
  
  // Update active chip
  document.querySelectorAll('.crm-filters .chip').forEach(chip => {
    chip.classList.remove('active');
    if (chip.dataset.filter === filter) {
      chip.classList.add('active');
    }
  });
  
  // Load filtered comments
  if (filter === 'all') {
    loadCRMComments();
  } else {
    loadCRMComments(filter);
  }
}

// Render CRM comments
function renderCRMComments() {
  const container = document.getElementById('crmCommentsList');
  
  if (crmComments.length === 0) {
    container.innerHTML = `
      <div class="empty-card">
        <p>No CRM comments found</p>
      </div>
    `;
    return;
  }
  
  container.innerHTML = crmComments.map(comment => `
    <div class="crm-comment-card ${comment.resolution_status}" onclick="viewCRMComment(${comment.id})">
      <div class="crm-card-header">
        <div class="crm-card-rep">
          <div class="crm-card-rep-avatar" style="background: ${comment.rep?.color || '#007AFF'}; color: white;">
            ${comment.rep?.avatar || '?'}
          </div>
          <div class="crm-card-rep-info">
            <h3>${comment.rep?.name || 'Unknown Rep'}</h3>
            <p>${comment.customer?.name || `Customer ${comment.crm_comp_code}`}</p>
          </div>
        </div>
        <div class="crm-card-meta">
          <div class="crm-card-date">${formatDate(comment.comment_date)}</div>
          <div class="pill ${comment.resolution_status}">
            ${comment.resolution_status.replace('_', ' ')}
          </div>
        </div>
      </div>
      
      <div class="crm-card-body">
        <div class="crm-card-text">${comment.raw_text}</div>
        ${comment.processed_summary ? `
          <div class="crm-card-summary">
            AI Summary: ${comment.processed_summary}
          </div>
        ` : ''}
      </div>
      
      <div class="crm-card-footer">
        <div class="crm-card-actions">
          ${comment.resolution_status === 'pending' ? `
            <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); processComment(${comment.id})">
              Process Now
            </button>
          ` : ''}
          ${comment.conversation_id ? `
            <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation(); viewConversation('${comment.conversation_id}')">
              View Conversation
            </button>
          ` : ''}
        </div>
      </div>
    </div>
  `).join('');
}

// Process single comment
async function processComment(commentId) {
  try {
    const res = await fetch(`/api/crm/comments/${commentId}/process`, { method: 'POST' });
    const data = await res.json();
    
    if (res.ok) {
      // Reload comments
      await loadCRMComments();
      await loadCRMSyncStatus();
    } else {
      alert('Failed to process comment');
    }
  } catch (error) {
    console.error('Failed to process comment:', error);
    alert('Failed to process comment');
  }
}

// Process all pending comments
async function processAllPending() {
  if (!confirm('Process all pending CRM comments? This may take a while.')) {
    return;
  }
  
  try {
    const res = await fetch('/api/crm/process-all', { method: 'POST' });
    const data = await res.json();
    
    if (data.status === 'ok') {
      alert(data.message);
      await loadCRMComments();
      await loadCRMSyncStatus();
    } else {
      alert('Failed to process comments');
    }
  } catch (error) {
    console.error('Failed to process all pending:', error);
    alert('Failed to process comments');
  }
}

// View CRM comment details
function viewCRMComment(commentId) {
  // TODO: Implement modal or detail view
  console.log('View comment:', commentId);
}

// View conversation
function viewConversation(conversationId) {
  switchView('viewInbox');
  // TODO: Select the conversation in the inbox
}

// Update next sync time
function updateNextSyncTime() {
  const lastSyncText = document.getElementById('lastSyncTime').textContent;
  if (lastSyncText === 'Never') {
    document.getElementById('nextSyncTime').textContent = 'Soon';
    return;
  }
  
  // Calculate next sync (60 minutes from last sync)
  // This is approximate - actual sync is handled by backend scheduler
  document.getElementById('nextSyncTime').textContent = 'Within 1 hour';
}

// Format relative time
function formatRelativeTime(date) {
  const now = new Date();
  const diff = now - date;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
}

// Format date
function formatDate(dateStr) {
  if (!dateStr) return 'Unknown';
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  } catch {
    return dateStr;
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  initCRMSync();
});
```

## Implementation Steps

1. ✅ **Backend Updates** (COMPLETED)
   - Modified CRM API for incremental sync
   - Added sync status endpoint
   - Updated environment configuration

2. **Frontend Updates** (TO DO)
   - Add sync button to topbar
   - Add CRM tab to navigation
   - Create CRM comments view
   - Add CSS styles
   - Add JavaScript functions
   - Test all functionality

## Testing Checklist

- [ ] Manual sync button works
- [ ] Sync status displays correctly
- [ ] CRM comments load and display
- [ ] Filtering works (all, pending, resolved, etc.)
- [ ] Process single comment works
- [ ] Process all pending works
- [ ] Auto-sync runs every 60 minutes
- [ ] Incremental sync only fetches new comments
- [ ] UI updates after sync
- [ ] Error handling works

## API Endpoints Used

- `GET /api/crm/sync-status` - Get sync status and counts
- `POST /api/crm/sync` - Manual sync (incremental by default)
- `GET /api/crm/comments?status=X&limit=Y` - List comments
- `POST /api/crm/comments/{id}/process` - Process single comment
- `POST /api/crm/process-all` - Process all pending

## Notes

- Background sync runs automatically every 60 minutes (configured in `.env`)
- Incremental sync only fetches comments since last sync
- Manual sync can override with `hours_back` parameter
- All sync operations update the `last_crm_sync` setting in database
- Frontend refreshes sync status every 30 seconds

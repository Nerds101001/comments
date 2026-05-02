/**
 * Frontend Updates for Rep Selector and Pagination
 * Add this code to frontend/index.html
 */

// ============================================================
// NEW: Rep Selector and Pagination State
// ============================================================
let allReps = [];
let repTypes = [];
let currentFilters = {
  rep_type: '',
  rep_id: '',
  handler: '',
  limit: 500,
  offset: 0
};
let totalConversations = 0;

// ============================================================
// NEW: Load Reps from API
// ============================================================
async function loadReps() {
  try {
    const response = await fetch('/api/reps');
    if (response.ok) {
      allReps = await response.json();
      populateRepSelector(allReps);
    }
    
    const typesResponse = await fetch('/api/reps/types');
    if (typesResponse.ok) {
      const data = await typesResponse.json();
      repTypes = data.types;
      updateCategoryFilters();
    }
  } catch (e) {
    console.error("Failed to load reps:", e);
  }
}

// ============================================================
// NEW: Populate Rep Selector Dropdown
// ============================================================
function populateRepSelector(reps) {
  const selector = document.getElementById('rep-selector');
  if (!selector) return;
  
  selector.innerHTML = '<option value="">All Representatives</option>';
  
  // Group by rep type
  const byType = {};
  reps.forEach(rep => {
    if (!byType[rep.rep_type]) {
      byType[rep.rep_type] = [];
    }
    byType[rep.rep_type].push(rep);
  });
  
  // Add optgroups
  Object.keys(byType).sort().forEach(type => {
    const optgroup = document.createElement('optgroup');
    optgroup.label = type.toUpperCase();
    
    byType[type].forEach(rep => {
      const option = document.createElement('option');
      option.value = rep.id;
      option.textContent = `${rep.name} (${rep.conversation_count})`;
      optgroup.appendChild(option);
    });
    
    selector.appendChild(optgroup);
  });
}

// ============================================================
// NEW: Update Category Filter Chips
// ============================================================
function updateCategoryFilters() {
  const container = document.getElementById('category-filters');
  if (!container) return;
  
  container.innerHTML = `
    <button class="chip active" data-rep-type="" onclick="filterByRepType('')">
      All (${totalConversations})
    </button>
  `;
  
  repTypes.forEach(type => {
    const btn = document.createElement('button');
    btn.className = 'chip';
    btn.dataset.repType = type.type;
    btn.textContent = `${type.type.charAt(0).toUpperCase() + type.type.slice(1)} (${type.conversation_count})`;
    btn.onclick = () => filterByRepType(type.type);
    container.appendChild(btn);
  });
}

// ============================================================
// NEW: Filter by Rep Type
// ============================================================
function filterByRepType(repType) {
  currentFilters.rep_type = repType;
  currentFilters.rep_id = '';
  currentFilters.offset = 0;
  
  // Update active state
  document.querySelectorAll('#category-filters .chip').forEach(chip => {
    chip.classList.toggle('active', chip.dataset.repType === repType);
  });
  
  // Update rep selector to show only reps of this type
  if (repType) {
    const filteredReps = allReps.filter(r => r.rep_type === repType);
    populateRepSelector(filteredReps);
  } else {
    populateRepSelector(allReps);
  }
  
  // Reset rep selector
  const selector = document.getElementById('rep-selector');
  if (selector) selector.value = '';
  
  // Load conversations
  loadConversationsWithFilters();
}

// ============================================================
// NEW: Filter by Specific Rep
// ============================================================
function filterByRep(repId) {
  currentFilters.rep_id = repId;
  currentFilters.offset = 0;
  loadConversationsWithFilters();
}

// ============================================================
// NEW: Load Conversations with Filters
// ============================================================
async function loadConversationsWithFilters() {
  try {
    // Build query string
    const params = new URLSearchParams();
    
    if (currentFilters.rep_id) {
      params.append('rep_id', currentFilters.rep_id);
    } else if (currentFilters.rep_type) {
      params.append('rep_type', currentFilters.rep_type);
    }
    
    if (currentFilters.handler && currentFilters.handler !== 'all') {
      params.append('handler', currentFilters.handler);
    }
    
    params.append('limit', currentFilters.limit);
    params.append('offset', currentFilters.offset);
    
    // Fetch conversations
    const response = await fetch(`/api/conversations?${params}`);
    if (response.ok) {
      const rawConvs = await response.json();
      conversations = rawConvs.map(c => ({
        ...c,
        senior_assigned: c.senior_assigned_id,
        fresh: c.is_fresh,
        messages: (c.messages || []).map(m => ({
          ...m,
          from: m.from_who,
          date: m.date_label,
          read: m.is_read
        }))
      }));
      
      // Update total count (approximate based on current results)
      totalConversations = conversations.length;
      
      // Render
      renderInbox();
      updatePaginationControls();
    }
  } catch (e) {
    console.error("Failed to load conversations:", e);
  }
}

// ============================================================
// NEW: Pagination Controls
// ============================================================
function goToPreviousPage() {
  if (currentFilters.offset > 0) {
    currentFilters.offset -= currentFilters.limit;
    loadConversationsWithFilters();
  }
}

function goToNextPage() {
  currentFilters.offset += currentFilters.limit;
  loadConversationsWithFilters();
}

function updatePaginationControls() {
  const prevBtn = document.getElementById('prev-page');
  const nextBtn = document.getElementById('next-page');
  const pageStart = document.getElementById('page-start');
  const pageEnd = document.getElementById('page-end');
  const totalCount = document.getElementById('total-count');
  
  if (!prevBtn || !nextBtn) return;
  
  // Update numbers
  if (pageStart) pageStart.textContent = currentFilters.offset + 1;
  if (pageEnd) pageEnd.textContent = Math.min(
    currentFilters.offset + currentFilters.limit,
    currentFilters.offset + conversations.length
  );
  if (totalCount) totalCount.textContent = '9,993'; // Total from backend
  
  // Enable/disable buttons
  prevBtn.disabled = currentFilters.offset === 0;
  nextBtn.disabled = conversations.length < currentFilters.limit;
}

// ============================================================
// MODIFIED: Update setFilter to use new system
// ============================================================
function setFilter(filter) {
  activeFilter = filter;
  currentFilters.handler = filter === 'all' ? '' : filter;
  currentFilters.offset = 0;
  
  // Update active state
  document.querySelectorAll('#filterChips .chip').forEach(chip => {
    chip.classList.toggle('active', chip.dataset.filter === filter);
  });
  
  loadConversationsWithFilters();
}

// ============================================================
// MODIFIED: Update loadData to use new system
// ============================================================
async function loadData() {
  try {
    // 1. Fetch Team (Reps)
    const teamRes = await fetch('/api/settings/team');
    if (teamRes.ok) {
      const teamArr = await teamRes.json();
      settings.team = {};
      teamArr.forEach(r => { settings.team[r.id] = r; });
    }

    // 2. Fetch Seniors
    const seniorsRes = await fetch('/api/settings/seniors');
    if (seniorsRes.ok) {
      const seniorsArr = await seniorsRes.json();
      settings.seniors = {};
      seniorsArr.forEach(s => { settings.seniors[s.id] = s; });
    }

    // 3. Load Reps for selector
    await loadReps();

    // 4. Fetch Conversations with filters
    await loadConversationsWithFilters();
    
    return;
  } catch (e) {
    console.error("Backend fetch failed", e);
  }
}

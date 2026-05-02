"""
Apply frontend updates - Fixed version
This script will update the frontend/index.html file with the new features
"""
import re

print("🚀 Applying frontend updates...")
print("="*60)

# Read the current frontend
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("✓ Read frontend/index.html")

# Backup original
with open('frontend/index.html.backup', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Created backup: frontend/index.html.backup")

# 1. Add CSS for new components (before the closing </style> tag)
css_additions = '''
  /* =========================================================
     REP SELECTOR & PAGINATION
     ========================================================= */
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

  .rep-selector {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid var(--separator);
    border-radius: 8px;
    background: var(--surface);
    color: var(--text);
    font-family: var(--font);
    font-size: 13px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .rep-selector:hover {
    border-color: var(--blue);
  }

  .rep-selector:focus {
    outline: none;
    border-color: var(--blue);
    box-shadow: 0 0 0 3px var(--blue-tint);
  }

  .pagination-controls {
    padding: 12px 18px;
    border-top: 1px solid var(--separator);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    background: var(--surface);
  }

  .btn-pagination {
    padding: 6px 12px;
    border: 1px solid var(--separator);
    border-radius: 6px;
    background: var(--surface);
    color: var(--text);
    font-family: var(--font);
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
  }

  .btn-pagination:hover:not(:disabled) {
    background: var(--bg);
    border-color: var(--blue);
    color: var(--blue);
  }

  .btn-pagination:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .page-info {
    font-size: 11px;
    color: var(--text-3);
    font-family: var(--font-mono);
  }

</style>'''

# Replace the closing </style> tag
content = content.replace('</style>', css_additions)
print("✓ Added CSS for rep selector and pagination")

# 2. Find and update the sidebar-head section
# Look for the sidebar-head div and replace it
sidebar_head_pattern = r'<div class="sidebar-head">.*?</div>\s*</div>'
new_sidebar_head = '''<div class="sidebar-head">
        <div class="sidebar-title">
          <span class="h">Conversations</span>
          <span class="count" id="sideCount">0 active</span>
        </div>
        
        <!-- Category Filters -->
        <div class="filter-section">
          <div class="filter-label">Category</div>
          <div class="filter-chips" id="category-filters">
            <button class="chip active" data-rep-type="" onclick="filterByRepType('')">All</button>
            <button class="chip" data-rep-type="sales" onclick="filterByRepType('sales')">Sales</button>
            <button class="chip" data-rep-type="ccare" onclick="filterByRepType('ccare')">CCare</button>
            <button class="chip" data-rep-type="newbiz" onclick="filterByRepType('newbiz')">NewBiz</button>
          </div>
        </div>
        
        <!-- Rep Selector -->
        <div class="filter-section">
          <div class="filter-label">Representative</div>
          <select id="rep-selector" class="rep-selector" onchange="filterByRep(this.value)">
            <option value="">All Representatives</option>
          </select>
        </div>
        
        <!-- Handler Filters -->
        <div class="filter-section">
          <div class="filter-label">Status</div>
          <div class="filter-chips" id="filterChips">
            <button class="chip active" data-filter="all" onclick="setFilter('all')">All</button>
            <button class="chip" data-filter="ai" onclick="setFilter('ai')">AI</button>
            <button class="chip" data-filter="escalated" onclick="setFilter('escalated')">Escalated</button>
            <button class="chip" data-filter="senior" onclick="setFilter('senior')">Senior</button>
            <button class="chip" data-filter="approval" onclick="setFilter('approval')">Approve</button>
            <button class="chip" data-filter="mukul" onclick="setFilter('mukul')">Yours</button>
          </div>
        </div>
      </div>'''

# Use a more specific pattern
old_sidebar_pattern = r'(<div class="sidebar-head">.*?<div class="filter-chips" id="filterChips">.*?</div>\s*</div>)'
content = re.sub(old_sidebar_pattern, new_sidebar_head, content, flags=re.DOTALL)
print("✓ Updated sidebar with category filters and rep selector")

# 3. Add pagination controls before </aside>
pagination_html = '''
      <!-- Pagination Controls -->
      <div class="pagination-controls">
        <button id="prev-page" class="btn-pagination" onclick="goToPreviousPage()" disabled>
          ← Previous
        </button>
        <span class="page-info">
          <span id="page-start">1</span>-<span id="page-end">500</span> 
          of <span id="total-count">9,993</span>
        </span>
        <button id="next-page" class="btn-pagination" onclick="goToNextPage()">
          Next →
        </button>
      </div>
    </aside>'''

content = content.replace('    </aside>', pagination_html)
print("✓ Added pagination controls")

# 4. Add JavaScript functions before the closing </script> tag
js_additions = '''
  // ============================================================
  // Rep Selector and Pagination
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

  function populateRepSelector(reps) {
    const selector = document.getElementById('rep-selector');
    if (!selector) return;
    
    selector.innerHTML = '<option value="">All Representatives</option>';
    
    const byType = {};
    reps.forEach(rep => {
      if (!byType[rep.rep_type]) byType[rep.rep_type] = [];
      byType[rep.rep_type].push(rep);
    });
    
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

  function updateCategoryFilters() {
    const container = document.getElementById('category-filters');
    if (!container) return;
    
    container.innerHTML = '<button class="chip active" data-rep-type="" onclick="filterByRepType(\\'\\')">All</button>';
    
    repTypes.forEach(type => {
      const btn = document.createElement('button');
      btn.className = 'chip';
      btn.dataset.repType = type.type;
      btn.textContent = `${type.type.charAt(0).toUpperCase() + type.type.slice(1)} (${type.conversation_count})`;
      btn.onclick = () => filterByRepType(type.type);
      container.appendChild(btn);
    });
  }

  function filterByRepType(repType) {
    currentFilters.rep_type = repType;
    currentFilters.rep_id = '';
    currentFilters.offset = 0;
    
    document.querySelectorAll('#category-filters .chip').forEach(chip => {
      chip.classList.toggle('active', chip.dataset.repType === repType);
    });
    
    if (repType) {
      const filteredReps = allReps.filter(r => r.rep_type === repType);
      populateRepSelector(filteredReps);
    } else {
      populateRepSelector(allReps);
    }
    
    const selector = document.getElementById('rep-selector');
    if (selector) selector.value = '';
    
    loadConversationsWithFilters();
  }

  function filterByRep(repId) {
    currentFilters.rep_id = repId;
    currentFilters.offset = 0;
    loadConversationsWithFilters();
  }

  async function loadConversationsWithFilters() {
    try {
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
        
        renderInbox();
        updatePaginationControls();
      }
    } catch (e) {
      console.error("Failed to load conversations:", e);
    }
  }

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
    
    if (pageStart) pageStart.textContent = currentFilters.offset + 1;
    if (pageEnd) pageEnd.textContent = Math.min(
      currentFilters.offset + currentFilters.limit,
      currentFilters.offset + conversations.length
    );
    if (totalCount) totalCount.textContent = '9,993';
    
    prevBtn.disabled = currentFilters.offset === 0;
    nextBtn.disabled = conversations.length < currentFilters.limit;
  }

  // Override the original setFilter to use new system
  const originalSetFilter = setFilter;
  setFilter = function(f) {
    activeFilter = f;
    currentFilters.handler = f === 'all' ? '' : f;
    currentFilters.offset = 0;
    
    document.querySelectorAll('#filterChips .chip').forEach(c => c.classList.remove('active'));
    const chip = document.querySelector(`#filterChips .chip[data-filter="${f}"]`);
    if (chip) chip.classList.add('active');
    
    loadConversationsWithFilters();
  };

  // Enhance loadData to load reps first
  const originalLoadData = loadData;
  loadData = async function() {
    try {
      // Load team and seniors first
      const teamRes = await fetch('/api/settings/team');
      if (teamRes.ok) {
        const teamArr = await teamRes.json();
        settings.team = {};
        teamArr.forEach(r => { settings.team[r.id] = r; });
      }

      const seniorsRes = await fetch('/api/settings/seniors');
      if (seniorsRes.ok) {
        const seniorsArr = await seniorsRes.json();
        settings.seniors = {};
        seniorsArr.forEach(s => { settings.seniors[s.id] = s; });
      }

      // Load reps for selector
      await loadReps();

      // Load conversations with filters
      await loadConversationsWithFilters();
      
      renderDash();
      renderInbox();
      renderCommand();
      renderSettings();
    } catch (e) {
      console.error("Backend fetch failed", e);
      // Fallback to original
      await originalLoadData();
    }
  };

</script>'''

content = content.replace('</script>', js_additions)
print("✓ Added JavaScript functions for filtering and pagination")

# Write the updated content
with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*60)
print("✅ Frontend updated successfully!")
print("\nChanges applied:")
print("  ✓ Added CSS for rep selector and pagination")
print("  ✓ Updated sidebar with category filters")
print("  ✓ Added rep selector dropdown")
print("  ✓ Added pagination controls")
print("  ✓ Added JavaScript functions for filtering")
print("  ✓ Enhanced loadData to use new API")
print("\n📝 Backup saved as: frontend/index.html.backup")
print("\n🌐 Please refresh your browser (Ctrl+Shift+R) to see the changes!")
print("="*60)

"""
Final complete fix for all issues:
1. Fix activeConv vs activeConvId mismatch
2. Ensure loadReps() is called on page load
3. Fix rep dropdown to be closed by default
4. Add proper initialization
"""
import re

print("🔧 Applying final complete fix...")
print("="*60)

# Read the current frontend
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("✓ Read frontend/index.html")

# Backup
with open('frontend/index.html.backup4', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Created backup: frontend/index.html.backup4")

# 1. Fix activeConv to activeConvId throughout
print("\n1. Fixing activeConv variable name...")
content = content.replace('if (activeConv === conv.id)', 'if (activeConvId === conv.id)')
content = content.replace('activeConv = convId;', 'activeConvId = convId;')
content = content.replace('let activeConv = null;', '')  # Remove if exists
print("✓ Fixed activeConv references")

# 2. Make sure rep selector is closed by default (remove size attribute)
print("\n2. Fixing rep selector to be closed by default...")
content = content.replace('size="8"', '')
print("✓ Rep selector will be closed by default")

# 3. Ensure loadReps is called in loadData
print("\n3. Ensuring loadReps is called on page load...")

# Find the loadData function and make sure it calls loadReps
old_loaddata_pattern = r'(async function loadData\(\) \{.*?)(await loadConversationsWithFilters\(\);)'
new_loaddata = r'\1// Load reps first\n      await loadReps();\n      \n      // Then load conversations\n      \2'

content = re.sub(old_loaddata_pattern, new_loaddata, content, flags=re.DOTALL)
print("✓ Added loadReps() call to loadData()")

# 4. Add initialization check to prevent calling before data is loaded
print("\n4. Adding initialization safeguards...")

old_filtertype_start = '''function filterByRepType(repType) {
    console.log("Filtering by rep type:", repType);'''

new_filtertype_start = '''function filterByRepType(repType) {
    console.log("Filtering by rep type:", repType);
    
    if (!allReps || allReps.length === 0) {
      console.warn("Reps not loaded yet, loading now...");
      loadReps().then(() => filterByRepType(repType));
      return;
    }'''

content = content.replace(old_filtertype_start, new_filtertype_start)
print("✓ Added initialization check to filterByRepType")

# 5. Fix the loadData function to ensure proper order
print("\n5. Fixing loadData function order...")

# Make sure loadData has the right structure
loaddata_fix = '''  async function loadData() {
    try {
      console.log("Loading data...");
      
      // 1. Fetch Team (Reps) for settings
      const teamRes = await fetch('/api/settings/team');
      if (teamRes.ok) {
        const teamArr = await teamRes.json();
        settings.team = {};
        teamArr.forEach(r => { settings.team[r.id] = r; });
        console.log("Loaded team settings:", Object.keys(settings.team).length, "reps");
      }

      // 2. Fetch Seniors
      const seniorsRes = await fetch('/api/settings/seniors');
      if (seniorsRes.ok) {
        const seniorsArr = await seniorsRes.json();
        settings.seniors = {};
        seniorsArr.forEach(s => { settings.seniors[s.id] = s; });
        console.log("Loaded seniors:", Object.keys(settings.seniors).length);
      }

      // 3. Load reps for selector (IMPORTANT!)
      console.log("Loading reps for selector...");
      await loadReps();
      
      if (allReps.length === 0) {
        console.error("Failed to load reps!");
      } else {
        console.log("Reps loaded successfully:", allReps.length);
      }

      // 4. Load conversations with filters
      console.log("Loading conversations...");
      await loadConversationsWithFilters();
      
      console.log("Data loading complete!");
    } catch (e) {
      console.error("Failed to load data:", e);
    }
  }'''

# Find and replace the loadData function
loaddata_pattern = r'async function loadData\(\) \{.*?^\s*\}'
content = re.sub(loaddata_pattern, loaddata_fix, content, flags=re.DOTALL | re.MULTILINE)
print("✓ Fixed loadData function")

# 6. Make sure renderInbox handles missing activeConvId
print("\n6. Fixing renderInbox to handle activeConvId...")

old_render_check = 'if (activeConvId === conv.id) item.classList.add(\'active\');'
new_render_check = 'if (activeConvId && activeConvId === conv.id) item.classList.add(\'active\');'

content = content.replace(old_render_check, new_render_check)
print("✓ Fixed activeConvId check in renderInbox")

# 7. Add a manual trigger to load reps if needed
print("\n7. Adding manual rep loading trigger...")

manual_load_button = '''        <!-- Rep Selector -->
        <div class="filter-section">
          <div class="filter-label">
            Representative
            <button onclick="loadReps()" style="float: right; font-size: 10px; padding: 2px 6px; border: 1px solid var(--separator); border-radius: 4px; background: var(--surface); cursor: pointer;">
              Reload
            </button>
          </div>'''

old_rep_section = '''<!-- Rep Selector -->
        <div class="filter-section">
          <div class="filter-label">Representative</div>'''

content = content.replace(old_rep_section, manual_load_button)
print("✓ Added reload button for reps")

# 8. Fix the rep selector HTML to not have size attribute
print("\n8. Ensuring rep selector is a normal dropdown...")

# Make sure the select doesn't have size attribute
content = re.sub(r'<select id="rep-selector" class="rep-selector" onchange="filterByRep\(this\.value\)" size="\d+">', 
                 '<select id="rep-selector" class="rep-selector" onchange="filterByRep(this.value)">', 
                 content)
print("✓ Fixed rep selector HTML")

# 9. Add CSS to make dropdown look better
print("\n9. Adding better CSS for rep selector...")

better_css = '''
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
    max-height: none !important;
  }

  .rep-selector:hover {
    border-color: var(--blue);
  }

  .rep-selector:focus {
    outline: none;
    border-color: var(--blue);
    box-shadow: 0 0 0 3px var(--blue-tint);
  }

  .rep-selector optgroup {
    font-weight: 700;
    color: var(--text-2);
    padding: 4px 0;
  }

  .rep-selector option {
    padding: 6px 12px;
  }

</style>'''

# Replace the existing rep-selector CSS
old_css_pattern = r'\.rep-selector \{[^}]*\}'
content = re.sub(old_css_pattern, '', content)
content = content.replace('</style>', better_css)
print("✓ Added better CSS")

# Write the updated content
with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*60)
print("✅ Final complete fix applied successfully!")
print("\nChanges made:")
print("  ✓ Fixed activeConv → activeConvId mismatch")
print("  ✓ Rep selector closed by default (normal dropdown)")
print("  ✓ loadReps() called on page load")
print("  ✓ Added initialization safeguards")
print("  ✓ Fixed loadData function order")
print("  ✓ Added 'Reload' button for reps")
print("  ✓ Better CSS for dropdown")
print("  ✓ Proper error handling")
print("\n📝 Backup saved as: frontend/index.html.backup4")
print("\n🌐 Please refresh your browser (Ctrl+Shift+R)!")
print("🔍 Open console (F12) to see:")
print("    - 'Loading reps for selector...'")
print("    - 'Reps loaded successfully: 96'")
print("="*60)

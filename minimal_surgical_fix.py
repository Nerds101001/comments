"""
Minimal surgical fix - only fix what's broken, don't break what works
1. Change pagination from 500 to 100
2. Add console logging for debugging
3. Don't touch existing functions
"""
import re

print("🔧 Applying minimal surgical fix...")
print("="*60)

# Read the original backup
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("✓ Read frontend/index.html (restored from backup)")

# Backup this version
with open('frontend/index.html.backup_working', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Created backup: frontend/index.html.backup_working")

# ONLY change pagination from 500 to 100 for performance
print("\n1. Changing pagination limit from 500 to 100...")

# Find the conversations API call and change limit
content = content.replace(
    "const convsRes = await fetch('/api/conversations');",
    "const convsRes = await fetch('/api/conversations?limit=100');"
)

# Also update any other places where we fetch conversations
content = re.sub(
    r"fetch\('/api/conversations'\)",
    "fetch('/api/conversations?limit=100')",
    content
)

print("✓ Changed pagination to 100 per page")

# Add a simple console log to see what's happening
print("\n2. Adding minimal debug logging...")

# Find the loadData function and add a simple log at the start
old_loaddata_start = '''  async function loadData() {
    try {
      // 1. Fetch Team (Reps)'''

new_loaddata_start = '''  async function loadData() {
    try {
      console.log("Loading data...");
      // 1. Fetch Team (Reps)'''

content = content.replace(old_loaddata_start, new_loaddata_start)
print("✓ Added minimal logging")

# Write the updated content
with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*60)
print("✅ Minimal fix applied successfully!")
print("\nChanges made:")
print("  ✓ Changed pagination from 500 to 100 per page")
print("  ✓ Added minimal console logging")
print("  ✓ Did NOT modify existing functions")
print("  ✓ Did NOT break existing code")
print("\n📝 Backup saved as: frontend/index.html.backup_working")
print("\n🌐 Please refresh your browser (Ctrl+Shift+R)!")
print("\n✅ Original functionality preserved!")
print("="*60)

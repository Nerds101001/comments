# How to Create WhatsApp Message Templates for AI Nudges

## Why We Need Templates

**Issue:** Custom text messages only work within 24-hour conversation windows in WhatsApp Business API.  
**Solution:** Create pre-approved message templates that can be sent anytime.

---

## Step 1: Go to Message Templates

1. **Open Meta Business Manager:**
   ```
   https://business.facebook.com/wa/manage/message-templates/
   ```

2. **Or via Developer Console:**
   ```
   https://developers.facebook.com/apps/974929091900005/whatsapp-business/wa-dev-console/
   ```
   - Click "Message Templates" in the left sidebar

---

## Step 2: Create Templates for Nudges

### Template 1: Morning Briefing

**Name:** `morning_briefing`  
**Category:** `UTILITY`  
**Language:** `English`

**Message:**
```
🌅 Good Morning {{1}}!

📊 Your Dashboard:
• Pending: {{2}} conversations
• High Priority: {{3}}
• Recent Activity: {{4}}

🎯 Top Priority: {{5}}

💪 Let's make today productive!

---
🤖 Hi-Tech AI Sales Assistant
```

**Variables:**
1. Rep name
2. Pending count
3. High priority count
4. Recent count
5. Top customer name

---

### Template 2: Daily Check-in

**Name:** `daily_checkin`  
**Category:** `UTILITY`  
**Language:** `English`

**Message:**
```
👋 Hi {{1}},

📊 Quick Update:
• Pending: {{2}} conversations
• Recent Activity: {{3}}

📋 Top Items:
{{4}}

✅ Keep up the great work!

---
🤖 Hi-Tech AI Sales Assistant
```

**Variables:**
1. Rep name
2. Pending count
3. Recent count
4. Top 3 customers (formatted list)

---

### Template 3: Urgent Alert

**Name:** `urgent_alert`  
**Category:** `UTILITY`  
**Language:** `English`

**Message:**
```
⚠️ {{1}}, Urgent Items!

🔥 {{2}} high priority conversations need attention:

{{3}}

⏰ Please review these ASAP!

---
🤖 Hi-Tech AI Sales Assistant
```

**Variables:**
1. Rep name
2. High priority count
3. List of urgent customers

---

### Template 4: Evening Summary

**Name:** `evening_summary`  
**Category:** `UTILITY`  
**Language:** `English`

**Message:**
```
🌆 End of Day Summary for {{1}}

✅ Today's Activity: {{2}} conversations
📋 Pending for Tomorrow: {{3}}

🎯 Priority Follow-ups:
{{4}}

👏 Great work today!

---
🤖 Hi-Tech AI Sales Assistant
```

**Variables:**
1. Rep name
2. Today's count
3. Pending count
4. Top priorities

---

## Step 3: Submit for Approval

1. **Fill in all template details**
2. **Add sample values** for each variable
3. **Click "Submit"**
4. **Wait for approval** (usually 15 minutes to 24 hours)

---

## Step 4: Once Approved

Once your templates are approved, I'll update the nudge system to use them instead of custom text.

The code will look like:

```python
# Send morning briefing template
payload = {
    "messaging_product": "whatsapp",
    "to": rep_phone,
    "type": "template",
    "template": {
        "name": "morning_briefing",
        "language": {"code": "en"},
        "components": [{
            "type": "body",
            "parameters": [
                {"type": "text", "text": rep_name},
                {"type": "text", "text": str(pending_count)},
                {"type": "text", "text": str(high_priority_count)},
                {"type": "text", "text": str(recent_count)},
                {"type": "text", "text": top_customer_name}
            ]
        }]
    }
}
```

---

## Alternative: Quick Test Template

If you want to test immediately, create a simple template:

**Name:** `sales_nudge`  
**Category:** `UTILITY`  
**Message:**
```
Hi {{1}}! You have {{2}} pending conversations. Please review them today.

---
Hi-Tech AI Sales
```

**Variables:**
1. Rep name
2. Pending count

This simple template will let us test the system right away!

---

## What to Do Now

**Option A: Create Templates (Recommended)**
1. Go to Message Templates
2. Create the 4 templates above
3. Submit for approval
4. Let me know when approved
5. I'll update the code to use templates

**Option B: Go Live (2-3 weeks)**
1. Submit app for review
2. Get approved for production
3. Send custom text without restrictions
4. No templates needed

**Option C: Test with Simple Template (Quick)**
1. Create just the `sales_nudge` template
2. Get it approved (15 mins - 24 hours)
3. Test immediately
4. Add more templates later

---

## Which Option Do You Prefer?

Let me know and I'll help you proceed! 🚀

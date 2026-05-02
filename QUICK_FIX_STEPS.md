# QUICK FIX - Railway PostgreSQL Connection

## THE PROBLEM
Your app's DATABASE_URL has wrong syntax: `${{Postgres.RAILWAY_PRIVATE_DOMAIN}}`
Should be: `postgres.railway.internal`

## FIX NOW (2 minutes)

### Step 1: Update App Environment Variables
1. Go to Railway dashboard: https://railway.app
2. Click "sweet-education" project
3. Click your **web service** (NOT PostgreSQL)
4. Click **Variables** tab
5. Click **RAW Editor** button
6. **DELETE ALL** and paste this:

```
AI_API_KEY=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
AI_MODEL=openai/gpt-oss-120b
AI_BASE_URL=https://integrate.api.nvidia.com/v1
AI_PROVIDER=nvidia
WHATSAPP_PHONE_NUMBER_ID=1105349452662677
WHATSAPP_ACCESS_TOKEN=EAA9EqzplgB4BReqyHSS8QReZBsxEmZBoSSfIukIAS5jbjyCd2ZCMvVjLzPpExXA5O4c603H8CgwKz5EV4VOIKvyD36vdRaKiRYSezVZC9yKFCwKpY25huQrRZAYbkcd4fLyabLZBs4Q4stzQuAw1ZCcxRkuTpZAhpD3MVvsBnPaWXBpB9cOC8W8KGLbZCnDTzwT52RY23c5c9KKyUcguBfDZBrpe5C2PRcaZChL6VVWFkGqKr1nRGjw3QiefpAp030csfn0jwPv48zKiuZBDR9k5ELI1AoKU
WHATSAPP_VERIFY_TOKEN=hitech-verify-2026
WHATSAPP_API_VERSION=v20.0
CRM_BASE_URL=https://api-crm.rustx.net
CRM_USERNAME=Nagender
CRM_PASSWORD=nag@8745
CRM_POLL_INTERVAL_MINUTES=60
MUKUL_PHONE=918264409000
MUKUL_NAME=Mukul Sareen
DATABASE_URL=postgresql+asyncpg://postgres:VNdQGmDBLKxTaXAFBTXRmpqEAsxynprm@postgres.railway.internal:5432/railway
APP_SECRET_KEY=hitech-ai-sales-secret-2026
DEBUG=false
```

7. Click **Update Variables**
8. App will auto-redeploy (wait 1-2 minutes)

### Step 2: Migrate Data (Choose ONE option)

#### OPTION A: Use CRM Sync API (EASIEST - 30 seconds)
Once app is running, visit these URLs in your browser:
1. `https://sweet-education-production.up.railway.app/api/crm/sync` (pulls all CRM data)
2. `https://sweet-education-production.up.railway.app/api/checkin/sync?days=90` (pulls check-ins)

#### OPTION B: Use Railway Web Shell (if Option A fails)
1. In Railway dashboard → web service → click **Shell** button (top right)
2. Wait for shell to open in browser
3. Run: `python migrate_to_postgresql.py`
4. Wait for migration to complete

### Step 3: Verify
Visit: `https://sweet-education-production.up.railway.app/api/dashboard/summary`

Should show **96 reps** instead of 5.

---

## What Was Wrong?
- Railway variable syntax `${{Postgres.RAILWAY_PRIVATE_DOMAIN}}` doesn't work in raw editor
- Must use actual hostname: `postgres.railway.internal`
- This is the internal DNS name Railway uses for PostgreSQL service

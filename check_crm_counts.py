"""
Check how many comments and check-ins the CRM has via admin account (Nagender, 1494).
"""
import asyncio
import httpx
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

CRM_BASE   = os.getenv("CRM_BASE_URL", "https://api-crm.rustx.net")
CRM_USER   = os.getenv("CRM_USERNAME", "")
CRM_PASS   = os.getenv("CRM_PASSWORD", "")
ADMIN_CODE = "1494"  # Nagender — admin with full data access


async def get_token() -> str:
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.post(
            f"{CRM_BASE}/api/Authentication/dologin",
            json={"username": CRM_USER, "password": CRM_PASS},
        )
        r.raise_for_status()
        d = r.json()
        token = d.get("token") or d.get("Token") or d.get("TokenKey") or d.get("access_token", "")
        if not token:
            raise RuntimeError(f"Login failed: {d}")
        print(f"✅ CRM login OK")
        return token


async def main():
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    today     = datetime.now()
    from_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")   # 1 year back
    to_date   = today.strftime("%Y-%m-%d")

    print(f"\n📅 Date range: {from_date} → {to_date}")
    print(f"👤 Admin emp_code: {ADMIN_CODE} (Nagender)\n")

    # ── 1. Comments via GetCustomersLastComment (latest comment per customer) ──
    print("─" * 55)
    print("1️⃣  GetCustomersLastComment (latest per customer, all reps)")
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.get(
            f"{CRM_BASE}/api/Reports/GetCustomersLastComment/{ADMIN_CODE}",
            headers=headers,
        )
        r.raise_for_status()
        d = r.json()
        comments_last = d.get("Data") or d.get("data") or (d if isinstance(d, list) else [])
        print(f"   → {len(comments_last):,} records (one latest comment per customer)")
        if comments_last:
            sample = comments_last[0]
            print(f"   Sample keys: {list(sample.keys())}")
            print(f"   Sample: EMP={sample.get('EMP_CODE')} COMP={sample.get('COMP_CODE')} "
                  f"Date={sample.get('CreatedOn')} Comment={str(sample.get('Comment',''))[:60]}")

    # ── 2. Comments via GetPipelineComment (date range, all history) ──────────
    print("\n─" * 55)
    print("2️⃣  GetPipelineComment (date range: last 365 days, admin)")
    from_dd = (today - timedelta(days=365)).strftime("%d-%m-%Y")
    to_dd   = today.strftime("%d-%m-%Y")
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.get(
            f"{CRM_BASE}/api/Comment/GetPipelineComment/{from_dd}/{to_dd}/{ADMIN_CODE}",
            headers=headers,
        )
        r.raise_for_status()
        d = r.json()
        if isinstance(d, list):
            pipeline_comments = d
        elif isinstance(d, dict):
            pipeline_comments = d.get("data") or d.get("Data") or d.get("Result") or []
            if not isinstance(pipeline_comments, list):
                pipeline_comments = []
        else:
            pipeline_comments = []
        print(f"   → {len(pipeline_comments):,} comments in last 365 days")
        print(f"   Raw response type: {type(d).__name__}, keys: {list(d.keys()) if isinstance(d, dict) else 'N/A'}")
        if pipeline_comments and isinstance(pipeline_comments[0], dict):
            sample = pipeline_comments[0]
            print(f"   Sample keys: {list(sample.keys())}")

    # ── 3. Check-ins via GetCheckinData (admin, last 365 days) ───────────────
    print("\n─" * 55)
    print("3️⃣  GetCheckinData (last 365 days, admin)")
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(
            f"{CRM_BASE}/api/Reports/GetCheckinData",
            headers=headers,
            json={"EmpCode": int(ADMIN_CODE), "StartDate": from_date, "EndDate": to_date},
        )
        r.raise_for_status()
        d = r.json()
        checkins = d.get("Data") or d.get("data") or (d if isinstance(d, list) else [])
        print(f"   → {len(checkins):,} check-in records in last 365 days")
        if checkins:
            sample = checkins[0]
            print(f"   Sample keys: {list(sample.keys())}")
            print(f"   Sample: EmpCode={sample.get('EmpCode')} CompCode={sample.get('CompCode')} "
                  f"Date={sample.get('CreatedonApp') or sample.get('Createdon')}")

    # ── 4. Check-ins last 30 days ─────────────────────────────────────────────
    print("\n─" * 55)
    print("4️⃣  GetCheckinData (last 30 days, admin)")
    from_30 = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(
            f"{CRM_BASE}/api/Reports/GetCheckinData",
            headers=headers,
            json={"EmpCode": int(ADMIN_CODE), "StartDate": from_30, "EndDate": to_date},
        )
        r.raise_for_status()
        d = r.json()
        checkins_30 = d.get("Data") or d.get("data") or (d if isinstance(d, list) else [])
        print(f"   → {len(checkins_30):,} check-in records in last 30 days")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "═" * 55)
    print("📊 CRM SUMMARY")
    print("═" * 55)
    print(f"  Latest comments (1 per customer) : {len(comments_last):>8,}")
    print(f"  Pipeline comments (365 days)     : {len(pipeline_comments):>8,}")
    print(f"  Check-ins (365 days)             : {len(checkins):>8,}")
    print(f"  Check-ins (30 days)              : {len(checkins_30):>8,}")
    print("═" * 55)


asyncio.run(main())

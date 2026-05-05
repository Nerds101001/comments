"""
Check total check-ins available in CRM
"""
import asyncio
import httpx
from datetime import datetime, timedelta
from app.config import settings


async def get_crm_token():
    """Get authentication token from CRM"""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{settings.CRM_BASE_URL}/api/Authentication/dologin",
            json={"username": settings.CRM_USERNAME, "password": settings.CRM_PASSWORD}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("TokenKey")


async def fetch_checkins(from_date: str, to_date: str):
    """Fetch check-ins from CRM"""
    token = await get_crm_token()
    
    url = f"{settings.CRM_BASE_URL}/api/Reports/GetCheckinData"
    payload = {
        "StartDate": from_date,
        "EndDate": to_date
    }
    
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, dict) and "Data" in data:
            return data["Data"] or []
        elif isinstance(data, list):
            return data
        else:
            return []


async def main():
    # Check last 90 days
    today = datetime.now()
    from_date_90 = (today - timedelta(days=90)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    print(f"Fetching check-ins from {from_date_90} to {to_date}...")
    checkins_90 = await fetch_checkins(from_date_90, to_date)
    print(f"✅ Last 90 days: {len(checkins_90)} check-ins")
    
    # Check last 180 days
    from_date_180 = (today - timedelta(days=180)).strftime("%Y-%m-%d")
    print(f"\nFetching check-ins from {from_date_180} to {to_date}...")
    checkins_180 = await fetch_checkins(from_date_180, to_date)
    print(f"✅ Last 180 days: {len(checkins_180)} check-ins")
    
    # Check last 365 days
    from_date_365 = (today - timedelta(days=365)).strftime("%Y-%m-%d")
    print(f"\nFetching check-ins from {from_date_365} to {to_date}...")
    checkins_365 = await fetch_checkins(from_date_365, to_date)
    print(f"✅ Last 365 days: {len(checkins_365)} check-ins")
    
    print(f"\n📊 Summary:")
    print(f"  - Database shows: 5,584 check-ins")
    print(f"  - CRM last 90 days: {len(checkins_90)} check-ins")
    print(f"  - CRM last 180 days: {len(checkins_180)} check-ins")
    print(f"  - CRM last 365 days: {len(checkins_365)} check-ins")


if __name__ == "__main__":
    asyncio.run(main())

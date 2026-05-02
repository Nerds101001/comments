"""
Sync check-in/check-out data from CRM to database
"""
import asyncio
from app.database import AsyncSessionLocal
from app.services.checkin_service import sync_checkin_data


async def main():
    print("Syncing Check-in Data from CRM")
    print("=" * 60)
    
    async with AsyncSessionLocal() as db:
        # Sync last 30 days
        result = await sync_checkin_data(db, days=30)
        
        print(f"\n✅ Sync Complete!")
        print(f"   Total Fetched: {result['total_fetched']}")
        print(f"   New Records: {result['total_new']}")
        print(f"   Updated Records: {result['total_updated']}")
        print(f"   Date Range: {result['from_date']} to {result['to_date']}")
        
        if result['errors']:
            print(f"\n⚠️  Errors:")
            for error in result['errors']:
                print(f"   - {error}")
        else:
            print(f"\n✅ No errors!")


if __name__ == "__main__":
    asyncio.run(main())

"""
Fetch CRM comments and save to file
"""
import asyncio
import httpx
import json
from datetime import datetime

CRM_BASE_URL = "https://api-crm.rustx.net"
CRM_USERNAME = "Nagender"
CRM_PASSWORD = "nag@8745"


async def get_token():
    """Login and get Bearer token"""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{CRM_BASE_URL}/api/Authentication/dologin",
            headers={"Content-Type": "application/json"},
            json={"username": CRM_USERNAME, "password": CRM_PASSWORD},
        )
        
        if resp.status_code != 200:
            raise RuntimeError(f"Login failed: {resp.text}")
        
        data = resp.json()
        token = data.get("token") or data.get("Token") or data.get("TokenKey") or data.get("access_token", "")
        
        if not token:
            raise RuntimeError(f"No token in response")
        
        print(f"✓ Authenticated as: {data.get('Data', {}).get('EMP_NAME', 'Unknown')}")
        print(f"✓ Token obtained: {token[:20]}...")
        return token


async def get_customers_last_comment(token, emp_code="1494"):
    """Fetch last comment for each customer"""
    print(f"\nFetching comments for employee {emp_code}...")
    
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(
            f"{CRM_BASE_URL}/api/Reports/GetCustomersLastComment/{emp_code}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        
        if resp.status_code != 200:
            raise RuntimeError(f"API error: {resp.text}")
        
        data = resp.json()
        comments = data.get("Data", [])
        
        print(f"✓ Fetched {len(comments)} comments")
        return comments


def display_comments(comments, limit=10):
    """Display sample comments"""
    print("\n" + "="*100)
    print(f"SAMPLE COMMENTS (showing {min(limit, len(comments))} of {len(comments)})")
    print("="*100)
    
    for i, comment in enumerate(comments[:limit], 1):
        print(f"\n{'─'*100}")
        print(f"Comment #{i}")
        print(f"{'─'*100}")
        print(f"Company Code: {comment.get('COMP_CODE')}")
        print(f"Company Name: {comment.get('COMP_NAME')}")
        print(f"City/State: {comment.get('CITY')}, {comment.get('STATE')}")
        print(f"Employee: {comment.get('EMP_NAME')} ({comment.get('EMP_CODE')}) - {comment.get('Designation')}")
        print(f"Date: {comment.get('CreatedOn')}")
        print(f"Comment: {comment.get('Comment')}")


def analyze_comments(comments):
    """Analyze comment statistics"""
    print("\n" + "="*100)
    print("COMMENT STATISTICS")
    print("="*100)
    
    # Count by designation
    designations = {}
    for c in comments:
        des = c.get('Designation', 'Unknown')
        designations[des] = designations.get(des, 0) + 1
    
    print(f"\nTotal Comments: {len(comments)}")
    print(f"\nBy Designation:")
    for des, count in sorted(designations.items(), key=lambda x: x[1], reverse=True):
        print(f"  {des}: {count}")
    
    # Count by state
    states = {}
    for c in comments:
        state = c.get('STATE', 'Unknown')
        states[state] = states.get(state, 0) + 1
    
    print(f"\nTop 10 States:")
    for state, count in sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {state}: {count}")
    
    # Recent comments
    recent = [c for c in comments if c.get('CreatedOn')]
    if recent:
        dates = [c.get('CreatedOn') for c in recent]
        print(f"\nDate Range:")
        print(f"  Oldest: {min(dates)}")
        print(f"  Newest: {max(dates)}")


async def main():
    print("="*100)
    print("CRM COMMENTS FETCHER")
    print("="*100)
    
    try:
        # Login
        token = await get_token()
        
        # Fetch comments
        comments = await get_customers_last_comment(token)
        
        # Display samples
        display_comments(comments, limit=20)
        
        # Analyze
        analyze_comments(comments)
        
        # Save to file
        output_file = "crm_comments_full.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(comments, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Full data saved to: {output_file}")
        
        # Save summary
        summary_file = "crm_comments_summary.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(f"CRM Comments Summary\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Comments: {len(comments)}\n\n")
            
            f.write("Sample Comments:\n")
            f.write("="*100 + "\n")
            for i, comment in enumerate(comments[:50], 1):
                f.write(f"\n{i}. {comment.get('COMP_NAME')} ({comment.get('CITY')})\n")
                f.write(f"   Employee: {comment.get('EMP_NAME')} - {comment.get('Designation')}\n")
                f.write(f"   Date: {comment.get('CreatedOn')}\n")
                f.write(f"   Comment: {comment.get('Comment')}\n")
        
        print(f"✓ Summary saved to: {summary_file}")
        
        print("\n" + "="*100)
        print("✓ SUCCESS - CRM DATA FETCHED")
        print("="*100)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

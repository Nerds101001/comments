"""
Export ALL CRM Comments from 2016 onwards to Excel
Fetches all comments from CRM API with emp_code, comp_code, dates, etc.
"""
import asyncio
import httpx
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

# CRM API Configuration
CRM_BASE_URL = os.getenv("CRM_BASE_URL", "https://api-crm.rustx.net")
CRM_USERNAME = os.getenv("CRM_USERNAME", "Nagender")
CRM_PASSWORD = os.getenv("CRM_PASSWORD", "nag@8745")

class CRMClient:
    def __init__(self):
        self.base_url = CRM_BASE_URL
        self.username = CRM_USERNAME
        self.password = CRM_PASSWORD
        self.token = None
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def login(self):
        """Get authentication token from CRM"""
        print("Logging into CRM...")
        try:
            response = await self.client.post(
                f"{self.base_url}/api/Authentication/dologin",
                json={
                    "username": self.username,
                    "password": self.password
                }
            )
            response.raise_for_status()
            data = response.json()
            # Token is in 'TokenKey' field, not 'token'
            self.token = data.get("TokenKey") or data.get("token")
            if self.token:
                print(f"Logged in successfully! Token: {self.token[:20]}...")
                return self.token
            else:
                print(f"No token in response: {data}")
                raise Exception("No token received from CRM")
        except Exception as e:
            print(f"Login failed: {e}")
            raise
    
    async def fetch_comments_for_date_range(self, start_date: str, end_date: str, emp_code: str = None) -> List[Dict]:
        """Fetch comments for a specific date range using the Comments Report endpoint"""
        if not self.token:
            await self.login()
        
        # Use the POST endpoint for comments report
        url = f"{self.base_url}/api/Reports/GetCommentsReport"
        
        body = {
            "fromDate": start_date,
            "toDate": end_date
        }
        if emp_code:
            body["empCode"] = emp_code
        
        print(f"Fetching comments: {start_date} to {end_date}" + (f" (emp: {emp_code})" if emp_code else " (all employees)"))
        
        try:
            response = await self.client.post(
                url,
                headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
                json=body
            )
            response.raise_for_status()
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list):
                comments = data
            else:
                # Check for Data field first (even if empty list)
                if "Data" in data:
                    comments = data["Data"]
                elif "data" in data:
                    comments = data["data"]
                elif "Result" in data and isinstance(data["Result"], list):
                    comments = data["Result"]
                else:
                    comments = []
            
            if isinstance(comments, list):
                if len(comments) > 0:
                    print(f"   Got {len(comments)} comments")
                return comments
            else:
                print(f"   Unexpected response format: {type(comments)}")
                return []
        except Exception as e:
            print(f"   Error: {e}")
            return []
    
    async def fetch_all_employees(self) -> List[str]:
        """Fetch list of all employee codes"""
        # You can get this from your database or CRM
        # For now, we'll fetch comments without emp_code filter to get all
        return []
    
    async def close(self):
        await self.client.aclose()


async def fetch_all_comments_from_2016():
    """Fetch all CRM comments from 2016 to now"""
    client = CRMClient()
    all_comments = []
    
    try:
        # Login first
        await client.login()
        
        # Generate date ranges (monthly chunks to avoid timeouts)
        start_year = 2016
        current_date = datetime.now()
        
        # Create monthly date ranges
        date_ranges = []
        for year in range(start_year, current_date.year + 1):
            for month in range(1, 13):
                # Skip future months
                if year == current_date.year and month > current_date.month:
                    break
                
                # First day of month
                start = datetime(year, month, 1)
                
                # Last day of month
                if month == 12:
                    end = datetime(year, 12, 31)
                else:
                    end = datetime(year, month + 1, 1) - timedelta(days=1)
                
                # Don't go beyond today
                if end > current_date:
                    end = current_date
                
                date_ranges.append((
                    start.strftime("%d-%m-%Y"),
                    end.strftime("%d-%m-%Y")
                ))
        
        print(f"\nTotal date ranges to fetch: {len(date_ranges)}")
        print(f"   From: {date_ranges[0][0]}")
        print(f"   To: {date_ranges[-1][1]}")
        print("\n" + "="*80)
        
        # Fetch comments for each date range
        for i, (start_date, end_date) in enumerate(date_ranges, 1):
            print(f"\n[{i}/{len(date_ranges)}] Processing {start_date} to {end_date}")
            
            comments = await client.fetch_comments_for_date_range(start_date, end_date)
            
            if comments:
                all_comments.extend(comments)
                print(f"   Total comments so far: {len(all_comments)}")
            
            # Small delay to avoid overwhelming the API
            await asyncio.sleep(0.5)
        
        print("\n" + "="*80)
        print(f"Fetching complete! Total comments: {len(all_comments)}")
        
        return all_comments
    
    finally:
        await client.close()


def export_to_excel(comments: List[Dict], filename: str = "crm_comments_export.xlsx"):
    """Export comments to Excel with all fields"""
    print(f"\nExporting {len(comments)} comments to Excel...")
    
    if not comments:
        print("No comments to export!")
        return
    
    # Flatten the data
    rows = []
    for comment in comments:
        row = {
            'Comment_ID': comment.get('COMMENT_AID'),
            'Employee_Code': comment.get('EMP_CODE'),
            'Employee_Name': comment.get('EMP_NAME'),
            'Designation': comment.get('DESIGNATION'),
            'Company_Code': comment.get('COMP_CODE'),
            'Company_Name': comment.get('COMP_NAME'),
            'Comment_Text': comment.get('COMMENT'),
            'Comment_Date': comment.get('CREATEDON'),
            'Financial_Year': comment.get('FYEAR'),
            'Status': comment.get('STATUS'),
            'Commented_By': comment.get('COMMENTED_BY'),
            'User_Type': comment.get('USER_TYPE'),
            'Set_On': comment.get('SETON'),
            'Ref_Comment_ID': comment.get('REF_COMMENT_ID'),
            'Checked': comment.get('CHECKED'),
            'Stages': comment.get('STAGES'),
            'Count_Comments': comment.get('CountComment'),
            'Count_Companies': comment.get('CountComp'),
        }
        rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Sort by date (newest first)
    df['Comment_Date'] = pd.to_datetime(df['Comment_Date'], errors='coerce')
    df = df.sort_values('Comment_Date', ascending=False)
    
    # Export to Excel
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Main sheet with all data
        df.to_excel(writer, sheet_name='All Comments', index=False)
        
        # Summary by Employee
        if 'Employee_Code' in df.columns:
            emp_summary = df.groupby(['Employee_Code', 'Employee_Name']).agg({
                'Comment_ID': 'count',
                'Company_Code': 'nunique'
            }).reset_index()
            emp_summary.columns = ['Employee_Code', 'Employee_Name', 'Total_Comments', 'Unique_Companies']
            emp_summary = emp_summary.sort_values('Total_Comments', ascending=False)
            emp_summary.to_excel(writer, sheet_name='By Employee', index=False)
        
        # Summary by Company
        if 'Company_Code' in df.columns:
            comp_summary = df.groupby(['Company_Code', 'Company_Name']).agg({
                'Comment_ID': 'count'
            }).reset_index()
            comp_summary.columns = ['Company_Code', 'Company_Name', 'Total_Comments']
            comp_summary = comp_summary.sort_values('Total_Comments', ascending=False)
            comp_summary.to_excel(writer, sheet_name='By Company', index=False)
        
        # Summary by Year
        df['Year'] = df['Comment_Date'].dt.year
        year_summary = df.groupby('Year').agg({
            'Comment_ID': 'count',
            'Employee_Code': 'nunique',
            'Company_Code': 'nunique'
        }).reset_index()
        year_summary.columns = ['Year', 'Total_Comments', 'Unique_Employees', 'Unique_Companies']
        year_summary = year_summary.sort_values('Year', ascending=False)
        year_summary.to_excel(writer, sheet_name='By Year', index=False)
        
        # Summary by Month (last 24 months)
        df['Year_Month'] = df['Comment_Date'].dt.to_period('M').astype(str)
        month_summary = df.groupby('Year_Month').agg({
            'Comment_ID': 'count'
        }).reset_index()
        month_summary.columns = ['Year_Month', 'Total_Comments']
        month_summary = month_summary.sort_values('Year_Month', ascending=False).head(24)
        month_summary.to_excel(writer, sheet_name='By Month', index=False)
    
    print(f"Excel file created: {filename}")
    print(f"\nSummary:")
    print(f"   Total Comments: {len(df)}")
    print(f"   Date Range: {df['Comment_Date'].min()} to {df['Comment_Date'].max()}")
    print(f"   Unique Employees: {df['Employee_Code'].nunique()}")
    print(f"   Unique Companies: {df['Company_Code'].nunique()}")
    print(f"\nSheets created:")
    print(f"   1. All Comments - Complete data")
    print(f"   2. By Employee - Summary per employee")
    print(f"   3. By Company - Summary per company")
    print(f"   4. By Year - Yearly summary")
    print(f"   5. By Month - Monthly summary (last 24 months)")


async def main():
    print("="*80)
    print("CRM COMMENTS EXPORT - FROM 2016 TO NOW")
    print("="*80)
    print(f"CRM URL: {CRM_BASE_URL}")
    print(f"Username: {CRM_USERNAME}")
    print("="*80)
    
    # Fetch all comments
    comments = await fetch_all_comments_from_2016()
    
    if comments:
        # Export to Excel
        filename = f"crm_comments_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        export_to_excel(comments, filename)
        
        print("\n" + "="*80)
        print("EXPORT COMPLETE!")
        print("="*80)
        print(f"File: {filename}")
        print(f"Total Comments: {len(comments)}")
    else:
        print("\nNo comments fetched!")


if __name__ == "__main__":
    # Install required package if not installed
    try:
        import pandas
        import openpyxl
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.run(["pip", "install", "pandas", "openpyxl"])
    
    asyncio.run(main())

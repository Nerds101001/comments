"""
Fetch ALL CRM data from API and export to Excel with dormant analysis
This fetches all historical data, not just what's in local database
"""
import asyncio
import httpx
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict

# CRM API Configuration
CRM_BASE_URL = "https://api-crm.rustx.net"
CRM_USERNAME = "Nagender"
CRM_PASSWORD = "nag@8745"

class CRMExporter:
    def __init__(self):
        self.base_url = CRM_BASE_URL
        self.username = CRM_USERNAME
        self.password = CRM_PASSWORD
        self.token = None
        self.client = httpx.AsyncClient(timeout=120.0)
    
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
            self.token = data.get("TokenKey") or data.get("token")
            if self.token:
                print(f"Logged in successfully!")
                return self.token
            else:
                raise Exception("No token received from CRM")
        except Exception as e:
            print(f"Login failed: {e}")
            raise
    
    async def fetch_all_employees(self) -> List[str]:
        """Get employee codes from local database"""
        print("\nGetting employee list from local database...")
        
        import sqlite3
        conn = sqlite3.connect('hitech_sales.db')
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT emp_code FROM reps WHERE emp_code IS NOT NULL ORDER BY emp_code')
        emp_codes = [str(row[0]) for row in cursor.fetchall()]
        conn.close()
        
        print(f"Found {len(emp_codes)} employees")
        return emp_codes
    
    async def fetch_comments_for_employee(self, emp_code: str, from_date: str, to_date: str) -> List[Dict]:
        """Fetch all comments for a specific employee in date range"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/Comment/GetPipelineComment/{from_date}/{to_date}/{emp_code}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                return data
            else:
                result = data.get("Data") or data.get("data") or []
                return result if isinstance(result, list) else []
        except Exception as e:
            return []
    
    async def fetch_all_comments(self) -> List[Dict]:
        """Fetch ALL comments from all employees across all time"""
        all_comments = []
        
        # Get employee list
        employees = await self.fetch_all_employees()
        
        # Define date ranges (yearly chunks from 2015 to now)
        current_year = datetime.now().year
        date_ranges = []
        
        for year in range(2015, current_year + 1):
            start = f"01-01-{year}"
            end = f"31-12-{year}"
            date_ranges.append((start, end))
        
        print(f"\nFetching comments for {len(employees)} employees across {len(date_ranges)} years...")
        print("="*80)
        
        total_fetched = 0
        
        for emp_idx, emp_code in enumerate(employees, 1):
            print(f"\n[Employee {emp_idx}/{len(employees)}] EMP_CODE: {emp_code}")
            
            for year_idx, (start_date, end_date) in enumerate(date_ranges, 1):
                year = start_date.split('-')[2]
                print(f"  [{year_idx}/{len(date_ranges)}] Year {year}...", end=" ")
                
                comments = await self.fetch_comments_for_employee(emp_code, start_date, end_date)
                
                if comments:
                    all_comments.extend(comments)
                    total_fetched += len(comments)
                    print(f"Got {len(comments)} comments (Total: {total_fetched})")
                else:
                    print("0 comments")
                
                # Small delay to avoid overwhelming API
                await asyncio.sleep(0.3)
        
        print("\n" + "="*80)
        print(f"Total comments fetched: {len(all_comments)}")
        return all_comments
    
    async def close(self):
        await self.client.aclose()


async def main():
    print("="*80)
    print("FETCHING ALL CRM DATA FROM API")
    print("="*80)
    
    exporter = CRMExporter()
    
    try:
        # Login
        await exporter.login()
        
        # Fetch all comments
        all_comments = await exporter.fetch_all_comments()
        
        if not all_comments:
            print("\nNo comments fetched!")
            return
        
        # Convert to DataFrame
        print(f"\nProcessing {len(all_comments)} comments...")
        
        rows = []
        for comment in all_comments:
            row = {
                'Comment_ID': comment.get('COMMENT_AID'),
                'Employee_Code': comment.get('EMP_CODE'),
                'Employee_Name': comment.get('EMP_NAME'),
                'Designation': comment.get('DESIGNATION'),
                'Company_Code': comment.get('COMP_CODE'),
                'Company_Name': comment.get('COMP_NAME'),
                'City': comment.get('CITY'),
                'State': comment.get('STATE'),
                'Comment_Text': comment.get('COMMENT'),
                'Comment_Date': comment.get('CREATEDON'),
                'Financial_Year': comment.get('FYEAR'),
                'Status': comment.get('STATUS'),
                'Commented_By': comment.get('COMMENTED_BY'),
                'User_Type': comment.get('USER_TYPE'),
                'Stages': comment.get('STAGES'),
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Parse dates
        df['Comment_Date_Parsed'] = pd.to_datetime(df['Comment_Date'], errors='coerce')
        
        # Get date range
        min_date = df['Comment_Date_Parsed'].min()
        max_date = df['Comment_Date_Parsed'].max()
        
        print(f"Date Range: {min_date} to {max_date}")
        
        # Export to Excel
        filename = f"crm_all_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        print(f"\nExporting to {filename}...")
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # All comments
            df.to_excel(writer, sheet_name='All Comments', index=False)
            
            # By Employee
            emp_summary = df.groupby(['Employee_Code', 'Employee_Name']).agg({
                'Comment_ID': 'count',
                'Company_Code': 'nunique'
            }).reset_index()
            emp_summary.columns = ['Employee_Code', 'Employee_Name', 'Total_Comments', 'Unique_Companies']
            emp_summary = emp_summary.sort_values('Total_Comments', ascending=False)
            emp_summary.to_excel(writer, sheet_name='By Employee', index=False)
            
            # By Company
            comp_summary = df.groupby(['Company_Code', 'Company_Name']).agg({
                'Comment_ID': 'count'
            }).reset_index()
            comp_summary.columns = ['Company_Code', 'Company_Name', 'Total_Comments']
            comp_summary = comp_summary.sort_values('Total_Comments', ascending=False)
            comp_summary.to_excel(writer, sheet_name='By Company', index=False)
            
            # By Year
            df['Year'] = df['Comment_Date_Parsed'].dt.year
            year_summary = df.groupby('Year').agg({
                'Comment_ID': 'count',
                'Employee_Code': 'nunique',
                'Company_Code': 'nunique'
            }).reset_index()
            year_summary.columns = ['Year', 'Total_Comments', 'Unique_Employees', 'Unique_Companies']
            year_summary = year_summary.sort_values('Year', ascending=False)
            year_summary.to_excel(writer, sheet_name='By Year', index=False)
            
            # By Month
            df['Year_Month'] = df['Comment_Date_Parsed'].dt.to_period('M').astype(str)
            month_summary = df.groupby('Year_Month').agg({
                'Comment_ID': 'count'
            }).reset_index()
            month_summary.columns = ['Year_Month', 'Total_Comments']
            month_summary = month_summary.sort_values('Year_Month', ascending=False)
            month_summary.to_excel(writer, sheet_name='By Month', index=False)
        
        print(f"\nExcel file created: {filename}")
        print(f"\nSummary:")
        print(f"   Total Comments: {len(df)}")
        print(f"   Date Range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
        print(f"   Unique Employees: {df['Employee_Code'].nunique()}")
        print(f"   Unique Companies: {df['Company_Code'].nunique()}")
        
        print("\n" + "="*80)
        print("EXPORT COMPLETE!")
        print("="*80)
        
    finally:
        await exporter.close()


if __name__ == "__main__":
    asyncio.run(main())

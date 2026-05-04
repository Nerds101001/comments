"""
Export CRM Comments from Local SQLite Database to Excel
This exports all the comments from your local hitech_sales.db for analysis
"""
import sqlite3
import pandas as pd
from datetime import datetime

print("="*80)
print("EXPORTING CRM COMMENTS FROM LOCAL DATABASE TO EXCEL")
print("="*80)

# Connect to local SQLite database
conn = sqlite3.connect('hitech_sales.db')

print("\nFetching all CRM comments...")

# Fetch all comments with related data
query = """
SELECT 
    c.crm_comment_id as 'Comment_ID',
    c.crm_emp_code as 'Employee_Code',
    r.name as 'Employee_Name',
    r.role as 'Role',
    c.crm_comp_code as 'Company_Code',
    cust.name as 'Company_Name',
    cust.city as 'City',
    cust.state as 'State',
    c.raw_text as 'Comment_Text',
    c.comment_date as 'Comment_Date',
    c.processed_summary as 'Processed_Summary',
    c.followup_question as 'Followup_Question',
    c.followup_sent as 'Followup_Sent',
    c.followup_sent_at as 'Followup_Sent_At',
    c.rep_reply as 'Rep_Reply',
    c.rep_reply_at as 'Rep_Reply_At',
    c.confidence_score as 'Confidence_Score',
    c.resolution_status as 'Resolution_Status',
    c.created_at as 'Created_At'
FROM crm_comments c
LEFT JOIN reps r ON c.crm_emp_code = r.emp_code
LEFT JOIN customers cust ON c.crm_comp_code = cust.comp_code
ORDER BY c.comment_date DESC
"""

df = pd.read_sql_query(query, conn)
print(f"Found {len(df)} comments")

if len(df) == 0:
    print("No comments found in database!")
    conn.close()
    exit()

# Create Excel file
filename = f"crm_comments_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
print(f"\nExporting to {filename}...")

with pd.ExcelWriter(filename, engine='openpyxl') as writer:
    # Main sheet with all data
    df.to_excel(writer, sheet_name='All Comments', index=False)
    
    # Summary by Employee
    emp_summary = df.groupby(['Employee_Code', 'Employee_Name']).agg({
        'Comment_ID': 'count',
        'Company_Code': 'nunique'
    }).reset_index()
    emp_summary.columns = ['Employee_Code', 'Employee_Name', 'Total_Comments', 'Unique_Companies']
    emp_summary = emp_summary.sort_values('Total_Comments', ascending=False)
    emp_summary.to_excel(writer, sheet_name='By Employee', index=False)
    
    # Summary by Company
    comp_summary = df.groupby(['Company_Code', 'Company_Name']).agg({
        'Comment_ID': 'count'
    }).reset_index()
    comp_summary.columns = ['Company_Code', 'Company_Name', 'Total_Comments']
    comp_summary = comp_summary.sort_values('Total_Comments', ascending=False)
    comp_summary.to_excel(writer, sheet_name='By Company', index=False)
    
    # Summary by Year
    df['Year'] = pd.to_datetime(df['Comment_Date'], errors='coerce').dt.year
    year_summary = df.groupby('Year').agg({
        'Comment_ID': 'count',
        'Employee_Code': 'nunique',
        'Company_Code': 'nunique'
    }).reset_index()
    year_summary.columns = ['Year', 'Total_Comments', 'Unique_Employees', 'Unique_Companies']
    year_summary = year_summary.sort_values('Year', ascending=False)
    year_summary.to_excel(writer, sheet_name='By Year', index=False)
    
    # Summary by Month (last 24 months)
    df['Year_Month'] = pd.to_datetime(df['Comment_Date'], errors='coerce').dt.to_period('M').astype(str)
    month_summary = df.groupby('Year_Month').agg({
        'Comment_ID': 'count'
    }).reset_index()
    month_summary.columns = ['Year_Month', 'Total_Comments']
    month_summary = month_summary.sort_values('Year_Month', ascending=False).head(24)
    month_summary.to_excel(writer, sheet_name='By Month', index=False)
    
    # Summary by City
    city_summary = df.groupby('City').agg({
        'Comment_ID': 'count',
        'Company_Code': 'nunique'
    }).reset_index()
    city_summary.columns = ['City', 'Total_Comments', 'Unique_Companies']
    city_summary = city_summary.sort_values('Total_Comments', ascending=False).head(50)
    city_summary.to_excel(writer, sheet_name='By City (Top 50)', index=False)
    
    # Summary by State
    state_summary = df.groupby('State').agg({
        'Comment_ID': 'count',
        'Company_Code': 'nunique',
        'Employee_Code': 'nunique'
    }).reset_index()
    state_summary.columns = ['State', 'Total_Comments', 'Unique_Companies', 'Unique_Employees']
    state_summary = state_summary.sort_values('Total_Comments', ascending=False)
    state_summary.to_excel(writer, sheet_name='By State', index=False)

conn.close()

print(f"Excel file created: {filename}")
print(f"\nSummary:")
print(f"   Total Comments: {len(df)}")
print(f"   Date Range: {df['Comment_Date'].min()} to {df['Comment_Date'].max()}")
print(f"   Unique Employees: {df['Employee_Code'].nunique()}")
print(f"   Unique Companies: {df['Company_Code'].nunique()}")
print(f"   Unique Cities: {df['City'].nunique()}")
print(f"   Unique States: {df['State'].nunique()}")

print(f"\nSheets created:")
print(f"   1. All Comments - Complete data with all fields")
print(f"   2. By Employee - Summary per employee")
print(f"   3. By Company - Summary per company")
print(f"   4. By Year - Yearly summary")
print(f"   5. By Month - Monthly summary (last 24 months)")
print(f"   6. By City (Top 50) - Top 50 cities by comment count")
print(f"   7. By State - Summary by state")

print("\n" + "="*80)
print("EXPORT COMPLETE!")
print("="*80)
print(f"File: {filename}")
print("\nYou can now open this Excel file for analysis!")

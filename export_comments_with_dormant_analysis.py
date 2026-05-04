"""
Export CRM Comments with Dormant Company Analysis
Shows companies with no comments in various time periods
"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

print("="*80)
print("EXPORTING CRM COMMENTS WITH DORMANT COMPANY ANALYSIS")
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

# Convert Comment_Date to datetime
df['Comment_Date_Parsed'] = pd.to_datetime(df['Comment_Date'], format='%m/%d/%Y %H:%M:%S', errors='coerce')

# Get actual date range
min_date = df['Comment_Date_Parsed'].min()
max_date = df['Comment_Date_Parsed'].max()
print(f"Date Range: {min_date} to {max_date}")

# Calculate cutoff dates
now = datetime.now()
cutoff_1_month = now - timedelta(days=30)
cutoff_3_months = now - timedelta(days=90)
cutoff_6_months = now - timedelta(days=180)
cutoff_1_year = now - timedelta(days=365)

print(f"\nAnalyzing dormant companies...")
print(f"  Reference date: {now.strftime('%Y-%m-%d')}")
print(f"  1 month ago: {cutoff_1_month.strftime('%Y-%m-%d')}")
print(f"  3 months ago: {cutoff_3_months.strftime('%Y-%m-%d')}")
print(f"  6 months ago: {cutoff_6_months.strftime('%Y-%m-%d')}")
print(f"  1 year ago: {cutoff_1_year.strftime('%Y-%m-%d')}")

# Get all companies
all_companies_query = """
SELECT 
    comp_code as 'Company_Code',
    name as 'Company_Name',
    city as 'City',
    state as 'State',
    cust_type as 'Customer_Type'
FROM customers
ORDER BY name
"""
all_companies = pd.read_sql_query(all_companies_query, conn)
print(f"\nTotal companies in database: {len(all_companies)}")

# Get last comment date for each company
last_comment_query = """
SELECT 
    c.crm_comp_code as 'Company_Code',
    MAX(c.comment_date) as 'Last_Comment_Date',
    COUNT(*) as 'Total_Comments'
FROM crm_comments c
GROUP BY c.crm_comp_code
"""
last_comments = pd.read_sql_query(last_comment_query, conn)
last_comments['Last_Comment_Date_Parsed'] = pd.to_datetime(
    last_comments['Last_Comment_Date'], 
    format='%m/%d/%Y %H:%M:%S', 
    errors='coerce'
)

# Merge with all companies
companies_with_last_comment = all_companies.merge(
    last_comments[['Company_Code', 'Last_Comment_Date', 'Last_Comment_Date_Parsed', 'Total_Comments']], 
    on='Company_Code', 
    how='left'
)

# Fill NaN for companies with no comments
companies_with_last_comment['Total_Comments'] = companies_with_last_comment['Total_Comments'].fillna(0).astype(int)

# Categorize companies
def categorize_dormancy(row):
    if pd.isna(row['Last_Comment_Date_Parsed']):
        return 'Never Contacted'
    elif row['Last_Comment_Date_Parsed'] < cutoff_1_year:
        return 'No Contact > 1 Year'
    elif row['Last_Comment_Date_Parsed'] < cutoff_6_months:
        return 'No Contact 6-12 Months'
    elif row['Last_Comment_Date_Parsed'] < cutoff_3_months:
        return 'No Contact 3-6 Months'
    elif row['Last_Comment_Date_Parsed'] < cutoff_1_month:
        return 'No Contact 1-3 Months'
    else:
        return 'Active (< 1 Month)'

companies_with_last_comment['Dormancy_Status'] = companies_with_last_comment.apply(categorize_dormancy, axis=1)

# Calculate days since last contact
def days_since_contact(row):
    if pd.isna(row['Last_Comment_Date_Parsed']):
        return 'Never'
    else:
        days = (now - row['Last_Comment_Date_Parsed']).days
        return days

companies_with_last_comment['Days_Since_Last_Contact'] = companies_with_last_comment.apply(days_since_contact, axis=1)

# Create dormancy reports
never_contacted = companies_with_last_comment[companies_with_last_comment['Dormancy_Status'] == 'Never Contacted']
no_contact_1_month = companies_with_last_comment[companies_with_last_comment['Dormancy_Status'] == 'No Contact 1-3 Months']
no_contact_3_months = companies_with_last_comment[companies_with_last_comment['Dormancy_Status'] == 'No Contact 3-6 Months']
no_contact_6_months = companies_with_last_comment[companies_with_last_comment['Dormancy_Status'] == 'No Contact 6-12 Months']
no_contact_1_year = companies_with_last_comment[companies_with_last_comment['Dormancy_Status'] == 'No Contact > 1 Year']

print(f"\nDormancy Analysis:")
print(f"  Never Contacted: {len(never_contacted)} companies")
print(f"  No Contact 1-3 Months: {len(no_contact_1_month)} companies")
print(f"  No Contact 3-6 Months: {len(no_contact_3_months)} companies")
print(f"  No Contact 6-12 Months: {len(no_contact_6_months)} companies")
print(f"  No Contact > 1 Year: {len(no_contact_1_year)} companies")

# Create Excel file
filename = f"crm_analysis_with_dormant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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
    df['Year'] = df['Comment_Date_Parsed'].dt.year
    year_summary = df.groupby('Year').agg({
        'Comment_ID': 'count',
        'Employee_Code': 'nunique',
        'Company_Code': 'nunique'
    }).reset_index()
    year_summary.columns = ['Year', 'Total_Comments', 'Unique_Employees', 'Unique_Companies']
    year_summary = year_summary.sort_values('Year', ascending=False)
    year_summary.to_excel(writer, sheet_name='By Year', index=False)
    
    # Summary by Month (last 24 months)
    df['Year_Month'] = df['Comment_Date_Parsed'].dt.to_period('M').astype(str)
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
    
    # DORMANT COMPANY SHEETS
    
    # All companies with last contact info
    companies_with_last_comment.to_excel(writer, sheet_name='All Companies Status', index=False)
    
    # Never Contacted
    never_contacted[['Company_Code', 'Company_Name', 'City', 'State', 'Customer_Type']].to_excel(
        writer, sheet_name='Never Contacted', index=False
    )
    
    # No Contact 1-3 Months
    no_contact_1_month[['Company_Code', 'Company_Name', 'City', 'State', 'Last_Comment_Date', 'Days_Since_Last_Contact', 'Total_Comments']].to_excel(
        writer, sheet_name='No Contact 1-3 Months', index=False
    )
    
    # No Contact 3-6 Months
    no_contact_3_months[['Company_Code', 'Company_Name', 'City', 'State', 'Last_Comment_Date', 'Days_Since_Last_Contact', 'Total_Comments']].to_excel(
        writer, sheet_name='No Contact 3-6 Months', index=False
    )
    
    # No Contact 6-12 Months
    no_contact_6_months[['Company_Code', 'Company_Name', 'City', 'State', 'Last_Comment_Date', 'Days_Since_Last_Contact', 'Total_Comments']].to_excel(
        writer, sheet_name='No Contact 6-12 Months', index=False
    )
    
    # No Contact > 1 Year
    no_contact_1_year[['Company_Code', 'Company_Name', 'City', 'State', 'Last_Comment_Date', 'Days_Since_Last_Contact', 'Total_Comments']].to_excel(
        writer, sheet_name='No Contact Over 1 Year', index=False
    )
    
    # Dormancy Summary
    dormancy_summary = companies_with_last_comment.groupby('Dormancy_Status').agg({
        'Company_Code': 'count'
    }).reset_index()
    dormancy_summary.columns = ['Dormancy_Status', 'Number_of_Companies']
    dormancy_summary.to_excel(writer, sheet_name='Dormancy Summary', index=False)

conn.close()

print(f"Excel file created: {filename}")
print(f"\nSummary:")
print(f"   Total Comments: {len(df)}")
print(f"   Date Range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
print(f"   Unique Employees: {df['Employee_Code'].nunique()}")
print(f"   Unique Companies: {df['Company_Code'].nunique()}")
print(f"   Total Companies in DB: {len(all_companies)}")

print(f"\nSheets created:")
print(f"   1. All Comments - Complete data with all fields")
print(f"   2. By Employee - Summary per employee")
print(f"   3. By Company - Summary per company")
print(f"   4. By Year - Yearly summary")
print(f"   5. By Month - Monthly summary (last 24 months)")
print(f"   6. By City (Top 50) - Top 50 cities by comment count")
print(f"   7. By State - Summary by state")
print(f"   8. All Companies Status - All companies with last contact date")
print(f"   9. Never Contacted - {len(never_contacted)} companies")
print(f"   10. No Contact 1-3 Months - {len(no_contact_1_month)} companies")
print(f"   11. No Contact 3-6 Months - {len(no_contact_3_months)} companies")
print(f"   12. No Contact 6-12 Months - {len(no_contact_6_months)} companies")
print(f"   13. No Contact Over 1 Year - {len(no_contact_1_year)} companies")
print(f"   14. Dormancy Summary - Overview of all dormancy categories")

print("\n" + "="*80)
print("EXPORT COMPLETE!")
print("="*80)
print(f"File: {filename}")
print("\nYou can now open this Excel file for comprehensive analysis!")
print("Use the dormant company sheets to identify companies that need attention!")

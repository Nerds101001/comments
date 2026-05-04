"""
Export CRM Comments from Railway PostgreSQL Database to Excel
This exports the comments that were already migrated to Railway
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import pandas as pd
from datetime import datetime

# Railway DATABASE_URL
DATABASE_URL = "postgresql+asyncpg://postgres:VNdQGmDBLKxTaXAFBTXRmpqEAsxynprm@postgres.railway.internal:5432/railway"

async def export_comments():
    print("="*80)
    print("EXPORTING CRM COMMENTS FROM RAILWAY DATABASE")
    print("="*80)
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Fetch all comments with related data
        print("\nFetching all CRM comments...")
        result = await session.execute(text("""
            SELECT 
                c.comment_id,
                c.emp_code,
                r.name as emp_name,
                r.designation,
                c.comp_code,
                cust.name as comp_name,
                cust.city,
                cust.state,
                c.comment_text,
                c.created_on,
                c.fyear,
                c.status,
                c.commented_by,
                c.user_type,
                c.set_on,
                c.ref_comment_id,
                c.checked,
                c.stages
            FROM crm_comments c
            LEFT JOIN reps r ON c.emp_code = r.emp_code
            LEFT JOIN customers cust ON c.comp_code = cust.comp_code
            ORDER BY c.created_on DESC
        """))
        
        rows = result.fetchall()
        print(f"Found {len(rows)} comments")
        
        if not rows:
            print("No comments found in database!")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=[
            'Comment_ID', 'Employee_Code', 'Employee_Name', 'Designation',
            'Company_Code', 'Company_Name', 'City', 'State',
            'Comment_Text', 'Comment_Date', 'Financial_Year',
            'Status', 'Commented_By', 'User_Type', 'Set_On',
            'Ref_Comment_ID', 'Checked', 'Stages'
        ])
        
        # Export to Excel
        filename = f"railway_crm_comments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        print(f"\nExporting to {filename}...")
        
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
        
        print("\n" + "="*80)
        print("EXPORT COMPLETE!")
        print("="*80)
        print(f"File: {filename}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(export_comments())

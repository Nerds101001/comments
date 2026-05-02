"""
Get the correct PostgreSQL URL for your app
"""

# Your PostgreSQL credentials
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "VNdQGmDBLKxTaXAFBTXRmpqEAsxynprm"
POSTGRES_DB = "railway"
POSTGRES_PORT = "5432"

print("=" * 80)
print("POSTGRESQL CONNECTION URL FOR YOUR APP")
print("=" * 80)

print("\n📋 Your PostgreSQL Credentials:")
print(f"   User: {POSTGRES_USER}")
print(f"   Password: {POSTGRES_PASSWORD}")
print(f"   Database: {POSTGRES_DB}")
print(f"   Port: {POSTGRES_PORT}")

print("\n" + "─" * 80)
print("🔍 You need to find the HOST from Railway")
print("─" * 80)

print("\n📝 Steps to get the HOST:")
print("1. Go to Railway Dashboard")
print("2. Click on PostgreSQL service")
print("3. Go to 'Connect' tab")
print("4. Look for 'Private Networking' or 'Internal URL'")
print("5. Copy the hostname (e.g., 'postgres.railway.internal')")

print("\n" + "─" * 80)
print("🎯 Once you have the HOST, your DATABASE_URL will be:")
print("─" * 80)

print("\nFormat:")
print("postgresql+asyncpg://postgres:VNdQGmDBLKxTaXAFBTXRmpqEAsxynprm@HOST:5432/railway")

print("\nExamples:")
print("─" * 80)
print("If HOST is 'postgres.railway.internal':")
print("postgresql+asyncpg://postgres:VNdQGmDBLKxTaXAFBTXRmpqEAsxynprm@postgres.railway.internal:5432/railway")

print("\nIf HOST is 'containers-us-west-123.railway.app':")
print("postgresql+asyncpg://postgres:VNdQGmDBLKxTaXAFBTXRmpqEAsxynprm@containers-us-west-123.railway.app:5432/railway")

print("\n" + "=" * 80)
print("📋 COPY THIS TO YOUR APP'S DATABASE_URL VARIABLE")
print("=" * 80)

print("\n🎯 Quick Method:")
print("─" * 80)
print("In your 'comments' service Variables, add:")
print("\nDATABASE_URL=postgresql+asyncpg://postgres:VNdQGmDBLKxTaXAFBTXRmpqEAsxynprm@${{Postgres.RAILWAY_PRIVATE_DOMAIN}}:5432/railway")

print("\n" + "=" * 80)

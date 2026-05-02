"""
Migrate data from SQLite to PostgreSQL
"""
import asyncio
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Base, Rep, Customer, Conversation, Message, Senior, CrmComment, CheckIn, StyleSample, StyleProfile, AppSetting
from app.database import AsyncSessionLocal

async def migrate_to_postgresql():
    print("=" * 80)
    print("MIGRATING FROM SQLITE TO POSTGRESQL")
    print("=" * 80)
    
    # Get PostgreSQL URL from environment
    postgres_url = os.getenv("DATABASE_URL")
    
    if not postgres_url:
        print("\n❌ DATABASE_URL not found in environment variables!")
        print("\nPlease set DATABASE_URL to your PostgreSQL connection string:")
        print("Example: postgresql+asyncpg://user:pass@host:5432/dbname")
        return
    
    # Convert postgres:// to postgresql:// if needed (Railway uses postgres://)
    if postgres_url.startswith("postgres://"):
        postgres_url = postgres_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif not postgres_url.startswith("postgresql+asyncpg://"):
        postgres_url = postgres_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    print(f"\n✅ PostgreSQL URL found")
    print(f"   Host: {postgres_url.split('@')[1].split('/')[0] if '@' in postgres_url else 'localhost'}")
    
    # Create PostgreSQL engine
    pg_engine = create_async_engine(postgres_url, echo=False)
    
    print("\n📊 Creating tables in PostgreSQL...")
    async with pg_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")
    
    # Create session
    PgSessionLocal = sessionmaker(pg_engine, class_=AsyncSession, expire_on_commit=False)
    
    # Migrate data
    print("\n📦 Migrating data from SQLite...")
    print("─" * 80)
    
    async with AsyncSessionLocal() as sqlite_db:
        async with PgSessionLocal() as pg_db:
            
            # Migrate Seniors
            print("Migrating seniors...")
            from sqlalchemy import select
            result = await sqlite_db.execute(select(Senior))
            seniors = result.scalars().all()
            for senior in seniors:
                pg_db.add(Senior(
                    id=senior.id,
                    name=senior.name,
                    emp_code=senior.emp_code,
                    phone=senior.phone,
                    role=senior.role
                ))
            await pg_db.commit()
            print(f"✅ Migrated {len(seniors)} seniors")
            
            # Migrate Reps
            print("Migrating reps...")
            result = await sqlite_db.execute(select(Rep))
            reps = result.scalars().all()
            for rep in reps:
                pg_db.add(Rep(
                    id=rep.id,
                    name=rep.name,
                    emp_code=rep.emp_code,
                    phone=rep.phone,
                    region=rep.region,
                    avatar=rep.avatar,
                    color=rep.color,
                    intensity=rep.intensity,
                    language=rep.language,
                    role=rep.role,
                    rep_type=rep.rep_type,
                    reports_to_id=rep.reports_to_id,
                    is_active=rep.is_active
                ))
            await pg_db.commit()
            print(f"✅ Migrated {len(reps)} reps")
            
            # Migrate Customers
            print("Migrating customers...")
            result = await sqlite_db.execute(select(Customer))
            customers = result.scalars().all()
            batch_size = 1000
            for i in range(0, len(customers), batch_size):
                batch = customers[i:i+batch_size]
                for customer in batch:
                    pg_db.add(Customer(
                        id=customer.id,
                        comp_code=customer.comp_code,
                        name=customer.name,
                        region=customer.region,
                        industry=customer.industry,
                        ltv=customer.ltv,
                        stage=customer.stage
                    ))
                await pg_db.commit()
                print(f"   Migrated {min(i+batch_size, len(customers))}/{len(customers)} customers")
            print(f"✅ Migrated {len(customers)} customers")
            
            # Migrate Conversations
            print("Migrating conversations...")
            result = await sqlite_db.execute(select(Conversation))
            conversations = result.scalars().all()
            for i in range(0, len(conversations), batch_size):
                batch = conversations[i:i+batch_size]
                for conv in batch:
                    pg_db.add(Conversation(
                        id=conv.id,
                        rep_id=conv.rep_id,
                        customer_id=conv.customer_id,
                        handler=conv.handler,
                        status=conv.status,
                        confidence_score=conv.confidence_score,
                        escalated_to_id=conv.escalated_to_id,
                        created_at=conv.created_at,
                        updated_at=conv.updated_at
                    ))
                await pg_db.commit()
                print(f"   Migrated {min(i+batch_size, len(conversations))}/{len(conversations)} conversations")
            print(f"✅ Migrated {len(conversations)} conversations")
            
            # Migrate Messages
            print("Migrating messages...")
            result = await sqlite_db.execute(select(Message))
            messages = result.scalars().all()
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i+batch_size]
                for msg in batch:
                    pg_db.add(Message(
                        id=msg.id,
                        conversation_id=msg.conversation_id,
                        sender=msg.sender,
                        text=msg.text,
                        sent_via=msg.sent_via,
                        sent_at=msg.sent_at,
                        delivered_at=msg.delivered_at,
                        read_at=msg.read_at
                    ))
                await pg_db.commit()
                print(f"   Migrated {min(i+batch_size, len(messages))}/{len(messages)} messages")
            print(f"✅ Migrated {len(messages)} messages")
            
            # Migrate CRM Comments
            print("Migrating CRM comments...")
            result = await sqlite_db.execute(select(CrmComment))
            comments = result.scalars().all()
            for i in range(0, len(comments), batch_size):
                batch = comments[i:i+batch_size]
                for comment in batch:
                    pg_db.add(CrmComment(
                        id=comment.id,
                        comment_aid=comment.comment_aid,
                        emp_code=comment.emp_code,
                        comp_code=comment.comp_code,
                        comment_text=comment.comment_text,
                        comment_date=comment.comment_date,
                        conversation_id=comment.conversation_id,
                        processed=comment.processed
                    ))
                await pg_db.commit()
                print(f"   Migrated {min(i+batch_size, len(comments))}/{len(comments)} comments")
            print(f"✅ Migrated {len(comments)} CRM comments")
            
            # Migrate Check-ins
            print("Migrating check-ins...")
            result = await sqlite_db.execute(select(CheckIn))
            checkins = result.scalars().all()
            for i in range(0, len(checkins), batch_size):
                batch = checkins[i:i+batch_size]
                for checkin in batch:
                    pg_db.add(CheckIn(
                        id=checkin.id,
                        emp_code=checkin.emp_code,
                        emp_name=checkin.emp_name,
                        comp_code=checkin.comp_code,
                        comp_name=checkin.comp_name,
                        checkin_date=checkin.checkin_date,
                        checkin_time=checkin.checkin_time,
                        checkout_time=checkin.checkout_time,
                        duration_minutes=checkin.duration_minutes,
                        latitude=checkin.latitude,
                        longitude=checkin.longitude,
                        address=checkin.address,
                        remarks=checkin.remarks
                    ))
                await pg_db.commit()
                print(f"   Migrated {min(i+batch_size, len(checkins))}/{len(checkins)} check-ins")
            print(f"✅ Migrated {len(checkins)} check-ins")
            
            # Migrate Style Samples
            print("Migrating style samples...")
            result = await sqlite_db.execute(select(StyleSample))
            samples = result.scalars().all()
            for sample in samples:
                pg_db.add(StyleSample(
                    id=sample.id,
                    senior_id=sample.senior_id,
                    sample_text=sample.sample_text,
                    source=sample.source,
                    created_at=sample.created_at
                ))
            await pg_db.commit()
            print(f"✅ Migrated {len(samples)} style samples")
            
            # Migrate Style Profiles
            print("Migrating style profiles...")
            result = await sqlite_db.execute(select(StyleProfile))
            profiles = result.scalars().all()
            for profile in profiles:
                pg_db.add(StyleProfile(
                    id=profile.id,
                    senior_id=profile.senior_id,
                    tone=profile.tone,
                    formality=profile.formality,
                    common_phrases=profile.common_phrases,
                    signature_style=profile.signature_style,
                    updated_at=profile.updated_at
                ))
            await pg_db.commit()
            print(f"✅ Migrated {len(profiles)} style profiles")
            
            # Migrate App Settings
            print("Migrating app settings...")
            result = await sqlite_db.execute(select(AppSetting))
            settings = result.scalars().all()
            for setting in settings:
                pg_db.add(AppSetting(
                    id=setting.id,
                    key=setting.key,
                    value=setting.value,
                    updated_at=setting.updated_at
                ))
            await pg_db.commit()
            print(f"✅ Migrated {len(settings)} app settings")
    
    print("\n" + "=" * 80)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 80)
    
    print("\n📊 Summary:")
    print("─" * 80)
    print(f"   Seniors: {len(seniors)}")
    print(f"   Reps: {len(reps)}")
    print(f"   Customers: {len(customers)}")
    print(f"   Conversations: {len(conversations)}")
    print(f"   Messages: {len(messages)}")
    print(f"   CRM Comments: {len(comments)}")
    print(f"   Check-ins: {len(checkins)}")
    print(f"   Style Samples: {len(samples)}")
    print(f"   Style Profiles: {len(profiles)}")
    print(f"   App Settings: {len(settings)}")
    print("─" * 80)
    
    print("\n🎯 Next Steps:")
    print("1. Update DATABASE_URL in Railway to use PostgreSQL")
    print("2. Redeploy your app")
    print("3. Verify data at: https://your-app.railway.app/api/dashboard/summary")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(migrate_to_postgresql())

"""
Migrate data from local SQLite to Railway PostgreSQL
Run this from your local machine
"""
import asyncio
import os
from sqlalchemy import create_engine, text, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Base, Rep, Customer, Conversation, Message, Senior, CRMComment, CheckIn, StyleSample, StyleProfile, AppSetting

async def migrate():
    print("=" * 80)
    print("MIGRATING LOCAL SQLITE → RAILWAY POSTGRESQL")
    print("=" * 80)
    
    # Local SQLite (source)
    sqlite_url = "sqlite+aiosqlite:///./hitech_sales.db"
    sqlite_engine = create_async_engine(sqlite_url, echo=False)
    SqliteSession = sessionmaker(sqlite_engine, class_=AsyncSession, expire_on_commit=False)
    
    # Railway PostgreSQL (destination) - PUBLIC URL for external access
    railway_url = "postgresql+asyncpg://postgres:VNdQGmDBLKxTaXAFBTXRmpqEAsxynprm@switchyard.proxy.rlwy.net:34827/railway"
    
    print(f"\n✅ Source: Local SQLite (hitech_sales.db)")
    print(f"✅ Destination: Railway PostgreSQL")
    
    pg_engine = create_async_engine(railway_url, echo=False)
    
    print("\n📊 Creating tables in Railway PostgreSQL...")
    async with pg_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")
    
    PgSession = sessionmaker(pg_engine, class_=AsyncSession, expire_on_commit=False)
    
    print("\n📦 Migrating data...")
    print("─" * 80)
    
    async with SqliteSession() as sqlite_db:
        async with PgSession() as pg_db:
            
            # Seniors
            print("Migrating seniors...")
            result = await sqlite_db.execute(select(Senior))
            seniors = result.scalars().all()
            for s in seniors:
                pg_db.add(Senior(
                    id=s.id,
                    name=s.name,
                    role=s.role,
                    phone=s.phone,
                    avatar=s.avatar,
                    color=s.color,
                    region=s.region,
                    language=s.language,
                    enabled=s.enabled
                ))
            await pg_db.commit()
            print(f"✅ {len(seniors)} seniors")
            
            # Reps
            print("Migrating reps...")
            result = await sqlite_db.execute(select(Rep))
            reps = result.scalars().all()
            for r in reps:
                pg_db.add(Rep(
                    id=r.id,
                    name=r.name,
                    emp_code=r.emp_code,
                    phone=r.phone,
                    region=r.region,
                    avatar=r.avatar,
                    color=r.color,
                    intensity=r.intensity,
                    language=r.language,
                    role=r.role,
                    rep_type=r.rep_type,
                    reports_to_id=r.reports_to_id,
                    is_active=r.is_active
                ))
            await pg_db.commit()
            print(f"✅ {len(reps)} reps")
            
            # Customers
            print("Migrating customers...")
            result = await sqlite_db.execute(select(Customer))
            customers = result.scalars().all()
            batch_size = 1000
            for i in range(0, len(customers), batch_size):
                batch = customers[i:i+batch_size]
                for c in batch:
                    pg_db.add(Customer(
                        id=c.id,
                        comp_code=c.comp_code,
                        name=c.name,
                        city=c.city,
                        state=c.state,
                        cust_type=c.cust_type,
                        last_order_days=c.last_order_days,
                        products_bought=c.products_bought,
                        ltv=c.ltv,
                        cross_sell=c.cross_sell,
                        phone=getattr(c, 'phone', None)
                    ))
                await pg_db.commit()
                print(f"   {min(i+batch_size, len(customers))}/{len(customers)}")
            print(f"✅ {len(customers)} customers")
            
            # Conversations
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
                        topic=conv.topic,
                        pipeline_stage=conv.pipeline_stage,
                        objective=conv.objective,
                        tactic=conv.tactic,
                        intel=getattr(conv, 'intel', None),
                        urgency=conv.urgency,
                        handler=conv.handler,
                        handler_reason=conv.handler_reason,
                        senior_assigned_id=conv.senior_assigned_id,
                        ai_confidence=conv.ai_confidence,
                        is_fresh=conv.is_fresh,
                        is_resolved=getattr(conv, 'is_resolved', False),
                        crm_ref=getattr(conv, 'crm_ref', None),
                        created_at=conv.created_at,
                        updated_at=conv.updated_at
                    ))
                await pg_db.commit()
                print(f"   {min(i+batch_size, len(conversations))}/{len(conversations)}")
            print(f"✅ {len(conversations)} conversations")
            
            # Messages
            print("Migrating messages...")
            result = await sqlite_db.execute(select(Message))
            messages = result.scalars().all()
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i+batch_size]
                for m in batch:
                    pg_db.add(Message(
                        id=m.id,
                        conversation_id=m.conversation_id,
                        from_who=m.from_who,
                        text=m.text,
                        ts=m.ts,
                        date_label=m.date_label,
                        status=m.status,
                        is_read=m.is_read,
                        by_ai=m.by_ai,
                        by_mukul_real=m.by_mukul_real,
                        requires_approval=m.requires_approval,
                        whatsapp_msg_id=getattr(m, 'whatsapp_msg_id', None),
                        created_at=m.created_at
                    ))
                await pg_db.commit()
                print(f"   {min(i+batch_size, len(messages))}/{len(messages)}")
            print(f"✅ {len(messages)} messages")
            
            # CRM Comments
            print("Migrating CRM comments...")
            result = await sqlite_db.execute(select(CRMComment))
            comments = result.scalars().all()
            
            # Get all valid conversation IDs
            conv_result = await pg_db.execute(select(Conversation.id))
            valid_conv_ids = set(conv_result.scalars().all())
            
            skipped = 0
            for i in range(0, len(comments), batch_size):
                batch = comments[i:i+batch_size]
                for c in batch:
                    # Skip if conversation_id is invalid
                    if c.conversation_id and c.conversation_id not in valid_conv_ids:
                        skipped += 1
                        continue
                        
                    pg_db.add(CRMComment(
                        id=c.id,
                        crm_comment_id=c.crm_comment_id,
                        rep_id=c.rep_id,
                        customer_id=c.customer_id,
                        crm_emp_code=c.crm_emp_code,
                        crm_comp_code=c.crm_comp_code,
                        raw_text=c.raw_text,
                        comment_date=c.comment_date,
                        processed_summary=c.processed_summary,
                        followup_question=c.followup_question,
                        followup_sent=c.followup_sent,
                        followup_sent_at=c.followup_sent_at,
                        rep_reply=c.rep_reply,
                        rep_reply_at=c.rep_reply_at,
                        confidence_score=c.confidence_score,
                        resolution_status=c.resolution_status,
                        conversation_id=c.conversation_id,
                        created_at=c.created_at
                    ))
                await pg_db.commit()
                print(f"   {min(i+batch_size, len(comments))}/{len(comments)}")
            print(f"✅ {len(comments) - skipped} CRM comments (skipped {skipped} with invalid refs)")
            
            # Check-ins
            print("Migrating check-ins...")
            result = await sqlite_db.execute(select(CheckIn))
            checkins = result.scalars().all()
            for i in range(0, len(checkins), batch_size):
                batch = checkins[i:i+batch_size]
                for ch in batch:
                    pg_db.add(CheckIn(
                        id=ch.id,
                        emp_code=ch.emp_code,
                        emp_name=ch.emp_name,
                        comp_code=ch.comp_code,
                        comp_name=ch.comp_name,
                        checkin_date=ch.checkin_date,
                        checkin_time=ch.checkin_time,
                        checkout_time=ch.checkout_time,
                        duration_minutes=ch.duration_minutes,
                        latitude=ch.latitude,
                        longitude=ch.longitude,
                        address=ch.address,
                        remarks=ch.remarks,
                        comment_id=getattr(ch, 'comment_id', None),
                        created_at=ch.created_at,
                        updated_at=ch.updated_at
                    ))
                await pg_db.commit()
                print(f"   {min(i+batch_size, len(checkins))}/{len(checkins)}")
            print(f"✅ {len(checkins)} check-ins")
            
            # Style Samples
            print("Migrating style samples...")
            result = await sqlite_db.execute(select(StyleSample))
            samples = result.scalars().all()
            for s in samples:
                pg_db.add(StyleSample(
                    id=s.id,
                    source=s.source,
                    text=s.text,
                    rep_language=s.rep_language,
                    context_type=s.context_type,
                    approved=s.approved,
                    created_at=s.created_at
                ))
            await pg_db.commit()
            print(f"✅ {len(samples)} style samples")
            
            # Style Profiles
            print("Migrating style profiles...")
            result = await sqlite_db.execute(select(StyleProfile))
            profiles = result.scalars().all()
            for p in profiles:
                pg_db.add(StyleProfile(
                    id=p.id,
                    language_key=p.language_key,
                    summary=p.summary,
                    sample_count=p.sample_count,
                    generated_at=p.generated_at
                ))
            await pg_db.commit()
            print(f"✅ {len(profiles)} style profiles")
            
            # App Settings
            print("Migrating app settings...")
            result = await sqlite_db.execute(select(AppSetting))
            settings = result.scalars().all()
            for s in settings:
                pg_db.add(AppSetting(
                    key=s.key,
                    value=s.value,
                    updated_at=s.updated_at
                ))
            await pg_db.commit()
            print(f"✅ {len(settings)} app settings")
    
    print("\n" + "=" * 80)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 80)
    print(f"\n📊 Migrated:")
    print(f"   • {len(seniors)} seniors")
    print(f"   • {len(reps)} reps")
    print(f"   • {len(customers)} customers")
    print(f"   • {len(conversations)} conversations")
    print(f"   • {len(messages)} messages")
    print(f"   • {len(comments)} CRM comments")
    print(f"   • {len(checkins)} check-ins")
    print(f"   • {len(samples)} style samples")
    print(f"   • {len(profiles)} style profiles")
    print(f"   • {len(settings)} app settings")
    print("\n✅ Verify at: https://web-production-fa001.up.railway.app/api/dashboard/summary")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(migrate())

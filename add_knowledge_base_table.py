"""
Add AI Knowledge Base table to Railway PostgreSQL
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def add_knowledge_base_table():
    # Railway PostgreSQL PUBLIC URL
    railway_url = "postgresql+asyncpg://postgres:VNdQGmDBLKxTaXAFBTXRmpqEAsxynprm@switchyard.proxy.rlwy.net:34827/railway"
    
    engine = create_async_engine(railway_url, echo=False)
    
    print("=" * 80)
    print("ADDING AI KNOWLEDGE BASE TABLE")
    print("=" * 80)
    
    async with engine.begin() as conn:
        # Create ai_knowledge_base table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ai_knowledge_base (
                id SERIAL PRIMARY KEY,
                category VARCHAR(50) NOT NULL,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                language VARCHAR(30) DEFAULT 'all',
                priority INTEGER DEFAULT 5,
                is_active BOOLEAN DEFAULT TRUE,
                created_by VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        print("✅ ai_knowledge_base table created")
        
        # Create index on category
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_category 
            ON ai_knowledge_base(category);
        """))
        print("✅ Index on category created")
        
        # Create index on is_active
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_active 
            ON ai_knowledge_base(is_active);
        """))
        print("✅ Index on is_active created")
        
        # Insert sample knowledge entries
        await conn.execute(text("""
            INSERT INTO ai_knowledge_base (category, title, content, language, priority, created_by)
            VALUES 
            ('example_nudge', 'Follow-up on delayed dispatch', 
             'Ravi, the Sharma Industries dispatch — has it been raised? Confirm by EOD.', 
             'hinglish_80', 8, 'system'),
            ('example_nudge', 'Cross-sell opportunity', 
             'Vishal, Patil Engg is buying Rust-X regularly. Push Dr Bio dunnage proposal today, don''t wait.', 
             'hinglish_80', 8, 'system'),
            ('product_info', 'Rust-X Product Line', 
             'Rust-X 1337, 1338 are VCI (Volatile Corrosion Inhibitor) products. Used for metal protection during storage/transport. Key customers: auto components, engineering.', 
             'all', 9, 'system'),
            ('product_info', 'Dr Bio Range', 
             'Dr Bio is our compostable/biodegradable packaging line. Includes dunnage, bags, films. ESG-focused. Target: logistics, FMCG, exporters with sustainability mandates.', 
             'all', 9, 'system'),
            ('terminology', 'LTV Meaning', 
             'LTV = Lifetime Value. Annual revenue from customer. ₹20L+ = key account.', 
             'all', 7, 'system'),
            ('terminology', 'At-risk Customer', 
             'Customer who hasn''t ordered in 2x their normal cadence. Needs immediate attention to prevent churn.', 
             'all', 7, 'system'),
            ('guideline', 'Deadline Format', 
             'Always end nudges with clear deadline: "Confirm by EOD", "Update by tomorrow", "Revert by 6pm".', 
             'all', 10, 'system'),
            ('guideline', 'Tone for High Intensity Reps', 
             'For high-intensity reps: Be direct, push hard, ask follow-ups. They respond well to proactive nudges.', 
             'all', 8, 'system')
            ON CONFLICT DO NOTHING;
        """))
        print("✅ Sample knowledge entries inserted")
    
    print("\n" + "=" * 80)
    print("✅ AI KNOWLEDGE BASE TABLE ADDED!")
    print("=" * 80)
    print("\nYou can now manage AI training data at:")
    print("https://web-production-fa001.up.railway.app/api/knowledge/entries")

if __name__ == "__main__":
    asyncio.run(add_knowledge_base_table())

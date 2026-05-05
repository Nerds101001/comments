"""
Hi-Tech AI Sales Org — FastAPI application entry point.

Serves:
  - /api/*       — REST API
  - /            — Frontend (frontend/index.html)

On startup:
  1. Creates all database tables
  2. Seeds default team / senior / customer / conversation data if DB is empty
  3. Starts the CRM polling background job (APScheduler)
"""
from __future__ import annotations
import json
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.database import init_db, _enable_wal, AsyncSessionLocal
from app.models import Rep, Senior, Customer, Conversation, Message
from app.api import conversations, whatsapp, crm, gmail, settings_api, dashboard, checkin, rep_dashboard
from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger(__name__)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


# ─────────────────────────────────────────────────────────
#  STARTUP / SHUTDOWN
# ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Hi-Tech AI Sales Org starting…")
    await init_db()
    await _enable_wal()
    await _seed_if_empty()
    await _load_db_settings()
    _start_scheduler()
    # Run initial sync in background (don't block startup)
    import asyncio
    asyncio.create_task(_run_initial_sync())
    yield
    logger.info("Shutting down…")


async def _load_db_settings():
    """Load persisted settings (AiSensy key, etc.) from DB into runtime config."""
    from sqlalchemy import select as sa_select
    from app.models import AppSetting
    from app.config import settings as app_settings
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                sa_select(AppSetting).where(
                    AppSetting.key.in_(["aisensy_api_key", "aisensy_username"])
                )
            )
            rows = {r.key: r.value for r in result.scalars().all()}
            if rows.get("aisensy_api_key"):
                app_settings.AISENSY_API_KEY = rows["aisensy_api_key"]
                logger.info("AiSensy API key loaded from database")
            if rows.get("aisensy_username"):
                app_settings.AISENSY_USERNAME = rows["aisensy_username"]
    except Exception as exc:
        logger.warning("Could not load DB settings: %s", exc)


async def _run_initial_sync():
    """Run an initial CRM sync on startup to catch up on any missed data."""
    try:
        logger.info("Running initial CRM sync in background...")
        # Add a small delay to let the app fully start first
        import asyncio
        await asyncio.sleep(5)
        
        async with AsyncSessionLocal() as db:
            from app.api import crm as crm_api
            from app.api import checkin as checkin_api
            
            # Sync comments — last 48 hours via GetCommentsReport (admin 1494)
            result = await crm_api.sync_crm_comments(hours_back=48, days_back=None, emp_code=None, db=db)
            new_comments = result.data.get("new_comments", 0) if result.data else 0
            
            # Sync check-ins — last 7 days on startup
            checkin_result = await checkin_api.sync_checkin_data(days=7, db=db)
            new_checkins = checkin_result.data.get("total_new", 0) if checkin_result.data else 0
            
            logger.info(f"Initial sync completed: {new_comments} new comments, {new_checkins} new check-ins")
            
            # Process new comments
            if new_comments > 0:
                await crm_api.process_all_pending(db=db)
    except Exception as exc:
        logger.warning(f"Initial sync failed (will retry on schedule): {exc}")


async def _seed_if_empty():
    """Insert default team, seniors, customers and sample conversations if DB is empty."""
    async with AsyncSessionLocal() as db:
        rep_count = (await db.execute(select(Rep))).scalars().first()
        if rep_count:
            return  # already seeded

        logger.info("Empty database — seeding default data…")

        # Seniors
        seniors = [
            Senior(id="anthony", name="Anthony Joseph", role="Senior Sales Manager · West & South",
                   phone="919812346001", avatar="AJ", color="#5856D6",
                   region="West & South", language="english_only", enabled=True),
            Senior(id="ardaman", name="Ardaman Singh", role="Senior Sales Manager · North India",
                   phone="919812346002", avatar="AS", color="#AF52DE",
                   region="North India", language="hinglish_80", enabled=True),
        ]
        for s in seniors:
            db.add(s)

        # Reps
        reps = [
            Rep(id="r1", name="Vishal Dhanraj Patil", emp_code="1811", phone="919812345001",
                region="Pune", avatar="VP", color="#34C759",
                intensity="standard", language="hinglish_80", role="Sales Person", reports_to_id="anthony"),
            Rep(id="r2", name="Ravi Kumar Negi", emp_code="1752", phone="919812345002",
                region="North India", avatar="RN", color="#007AFF",
                intensity="high", language="hinglish_80", role="Sales Person", reports_to_id="ardaman"),
            Rep(id="r3", name="Girish Bijutkar", emp_code="1797", phone="919812345003",
                region="Maharashtra", avatar="GB", color="#FF9500",
                intensity="standard", language="hinglish_60", role="Sales Person", reports_to_id="anthony"),
            Rep(id="r4", name="Pradeep Vishwakarma", emp_code="1593", phone="919812345004",
                region="Mumbai/Gujarat", avatar="PV", color="#AF52DE",
                intensity="high", language="hinglish_80", role="Senior Sales Person", reports_to_id="anthony"),
            Rep(id="r5", name="Vikas Kamlakar", emp_code="1062", phone="919812345006",
                region="Karnataka", avatar="VK", color="#5AC8FA",
                intensity="light", language="english_light_hindi", role="Sales Person", reports_to_id="anthony"),
            Rep(id="r6", name="D Daniel Raj", emp_code="1708", phone="919812345005",
                region="Tamil Nadu", avatar="DR", color="#FF3B30",
                intensity="standard", language="english_only", role="Sales Person", reports_to_id="anthony"),
        ]
        for r in reps:
            db.add(r)

        # Customers
        customers = [
            Customer(id="cu1", comp_code="5989", name="Patil Engineering Works",
                     city="Pune", state="Maharashtra", cust_type="regular", last_order_days=22,
                     products_bought=["Rust-X 1338"], ltv="₹14L/yr", cross_sell=["Dr Bio dunnage", "Tuffpaulin export"]),
            Customer(id="cu2", comp_code="56772", name="Sharma Industries",
                     city="Faridabad", state="Haryana", cust_type="new", last_order_days=None,
                     products_bought=[], ltv="first deal", cross_sell=[]),
            Customer(id="cu3", comp_code="55659", name="Asian Polytech",
                     city="Delhi", state="Delhi", cust_type="at_risk", last_order_days=65,
                     products_bought=["KIF sacks"], ltv="₹8L/yr (declining)", cross_sell=[]),
            Customer(id="cu4", comp_code="46698", name="Ravindra Plastics",
                     city="Mumbai", state="Maharashtra", cust_type="new", last_order_days=None,
                     products_bought=[], ltv="trial pending", cross_sell=["Biopolymer pellets"]),
            Customer(id="cu5", comp_code="53340", name="Coimbatore Footwear Ind",
                     city="Coimbatore", state="Tamil Nadu", cust_type="new", last_order_days=None,
                     products_bought=[], ltv="first contact", cross_sell=[]),
            Customer(id="cu6", comp_code="10339", name="Belgaum Auto Components",
                     city="Belgaum", state="Karnataka", cust_type="dormant", last_order_days=92,
                     products_bought=["VCI 2D bags", "Rust-X 1337"], ltv="₹22L/yr historical", cross_sell=[]),
            Customer(id="cu7", comp_code="40030", name="Mahindra Logistics Navi Mumbai",
                     city="Navi Mumbai", state="Maharashtra", cust_type="regular", last_order_days=18,
                     products_bought=["Tuffpaulin 250GSM", "Tuffpaulin 300GSM"], ltv="₹38L/yr",
                     cross_sell=["Dr Bio", "EVA packaging"]),
        ]
        for c in customers:
            db.add(c)

        await db.flush()  # get IDs before inserting conversations

        # Sample conversations
        seed_convs = [
            {
                "id": "conv1", "rep_id": "r1", "customer_id": "cu1",
                "topic": "VCI catalogue follow-up + Dr Bio cross-sell",
                "pipeline_stage": "Active customer · cross-sell window",
                "objective": "Get Dr Bio dunnage proposal sent today; confirm VCI catalogue dispatch",
                "tactic": "Acknowledge regular customer, push parallel cross-sell",
                "urgency": "medium", "handler": "ai", "ai_confidence": 88, "is_fresh": True,
                "messages": [
                    {"from_who": "mukul", "text": "Vishal, yesterday's Patil Engg visit was 45 min — that's solid. Customer asked about VCI bag sizes and Dr Bio dunnage. Catalogue toh aaj bhej diya?", "ts": "10:14", "date_label": "today", "status": "sent", "by_ai": True},
                    {"from_who": "rep", "text": "Sir catalogue 11am ko bhej diya, customer ne acknowledge bhi kiya. Monday tak revert karenge bole hain.", "ts": "11:32", "date_label": "today", "status": "received"},
                    {"from_who": "mukul", "text": "Achha. Now on Dr Bio dunnage — they're an existing customer, conversion will be fast. Aaj hi proposal bhejo, Monday tak wait mat karo. Run both deals in parallel. Confirm by EOD.", "ts": "11:45", "date_label": "today", "status": "draft", "by_ai": True},
                ],
            },
            {
                "id": "conv2", "rep_id": "r2", "customer_id": "cu3",
                "topic": "Drive-by anomaly + 15% discount demand",
                "pipeline_stage": "At-risk · pricing decision needed",
                "objective": "Decision on 15% discount or alternative bundle",
                "tactic": "Customer demanding 15% beyond 8% standard authority",
                "urgency": "high", "handler": "senior", "senior_assigned_id": "ardaman", "ai_confidence": 42,
                "handler_reason": "Pricing 15% beyond rep authority. AI routed to Ardaman first — North region escalation. He has 24h to resolve before it bumps to you.",
                "messages": [
                    {"from_who": "mukul", "text": "Ravi, this Asian Polytech visit — only 8 minutes? Comment says price discussion happened but 8 min mein toh proper meeting nahi hoti. What was the actual situation?", "ts": "17:30", "date_label": "yesterday", "status": "sent", "by_ai": True},
                    {"from_who": "rep", "text": "Sir actually customer busy tha, 10 min hi de paya. Said our KIF price is 12% high vs Asian Polymer, asked for 8% discount.", "ts": "18:02", "date_label": "yesterday", "status": "received"},
                    {"from_who": "mukul", "text": "Theek hai. But this customer hasn't ordered in 65 days — at-risk hai. Don't go discount route. Set up a proper plant demo — KIF tensile strength dikhao with samples. Wednesday tak ho jaana chahiye.", "ts": "09:12", "date_label": "today", "status": "sent", "by_ai": True},
                    {"from_who": "rep", "text": "Sir today 4pm appointment confirmed, demo done with samples. But customer ne final position liya — wants 15% discount, otherwise switching to Asian Polymer permanently.", "ts": "16:45", "date_label": "today", "status": "received"},
                ],
            },
            {
                "id": "conv4", "rep_id": "r4", "customer_id": "cu4",
                "topic": "Dr Bio 5-ton trial · Approval Pending",
                "pipeline_stage": "High-value trial conversion",
                "objective": "Lock trial PO; AI prepared message awaiting your sign-off",
                "tactic": "Message uses your name and pricing commitment — needs your OK",
                "urgency": "high", "handler": "approval", "ai_confidence": 71, "is_fresh": True,
                "handler_reason": "AI drafted reply that references your personal commitment to MOQ exception pricing. High-value trial (5T → 20T/mo potential) — wants your sign-off before send.",
                "messages": [
                    {"from_who": "mukul", "text": "Pradeep, Ravindra Plastics 5-ton trial deal hot hai. Owner ne next week decision bola hai. FSSAI docs and pricing approval ka kya status?", "ts": "20:14", "date_label": "yesterday", "status": "sent", "by_ai": True},
                    {"from_who": "rep", "text": "Sir FSSAI docs Friday tak mil jayenge, but pricing approval Heena ma'am side stuck hai — finance team ne hold kiya hai because trial volume below normal MOQ.", "ts": "08:30", "date_label": "today", "status": "received"},
                    {"from_who": "mukul", "text": "Pradeep, MOQ wala issue main personally Heena se baat karunga aaj. You focus on FSSAI side — make sure Friday tak hi mile, no slips. Trial pricing main approve kar dunga special case ke roop mein, but PO Monday tak chahiye warna deal ka leverage chala jaayega. Confirm karo by EOD.", "ts": "09:15", "date_label": "today", "status": "draft", "by_ai": True, "requires_approval": True},
                ],
            },
            {
                "id": "conv7", "rep_id": "r5", "customer_id": "cu6",
                "topic": "DORMANT — Belgaum Auto · Operational Failure",
                "pipeline_stage": "Win-back · operational complaint",
                "objective": "Customer left over Hi-Tech delivery failures — needs you",
                "tactic": "Customer cited 3 late dispatches from Manesar — beyond rep's scope",
                "urgency": "high", "handler": "escalated", "ai_confidence": 38,
                "handler_reason": "Customer cited Hi-Tech operational issue (delayed dispatch + wrong sizes from Heena's team) as switch reason. ₹22L/yr historical account. Win-back needs YOUR direct acknowledgement.",
                "messages": [
                    {"from_who": "mukul", "text": "Vikas, Belgaum Auto Components — this customer hasn't ordered in 92 days, vs their normal 30-day cadence. ₹22L/yr account, likely competitor switch. Phone first, no visit yet. Find out the exact reason. Update me by 6pm.", "ts": "11:08", "date_label": "yesterday", "status": "sent", "by_ai": True},
                    {"from_who": "rep", "text": "Sir, I called Mr. Patil. He said in the last 6 months we had 3 late dispatches and once wrong size came. They got frustrated with Manesar plant delivery, so shifted to Cortec. He told me — 'ab Hi-Tech pe trust nahi hai, sorry'.", "ts": "14:20", "date_label": "today", "status": "received"},
                ],
            },
            {
                "id": "conv8", "rep_id": "r4", "customer_id": "cu7",
                "topic": "CROSS-SELL · Mahindra Logistics",
                "pipeline_stage": "Active customer · strategic upsell",
                "objective": "Position Dr Bio + EVA at CXO level",
                "tactic": "Key ₹38L account — needs CEO-to-CEO ESG framing",
                "urgency": "low", "handler": "mukul", "ai_confidence": 65,
                "handler_reason": "You took this over — strategic key-account upsell needs your direct ESG positioning. AI on advisory standby.",
                "messages": [
                    {"from_who": "mukul", "text": "Pradeep, Mahindra Logistics Navi Mumbai — yeh ₹38L/yr Tuffpaulin customer hai. Logistics company hai, ESG pressure hoga. Kabhi inse Dr Bio compostable ya EVA dunnage discuss kiya?", "ts": "11:15", "date_label": "yesterday", "status": "sent", "by_ai": True},
                    {"from_who": "rep", "text": "Sir kabhi formally pitch nahi ki Dr Bio ki — they buy regularly so unko bother nahi karta tha. Lekin point sahi hai, ESG angle work kar sakta hai. Next week meeting set karu?", "ts": "15:20", "date_label": "yesterday", "status": "received"},
                    {"from_who": "mukul", "text": "Pradeep, main personally handle karunga is account ko. Tuesday afternoon meeting set karo, main aaunga along with you. Their procurement head Mr Iyer ko mujhe directly milna hai — ESG narrative aur 5-year framework I'll position myself. Tum slot lock karo.", "ts": "15:42", "date_label": "yesterday", "status": "sent", "by_ai": False, "by_mukul_real": True},
                ],
            },
        ]

        for conv_data in seed_convs:
            msgs = conv_data.pop("messages", [])
            conv = Conversation(
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                **{k: v for k, v in conv_data.items()},
            )
            db.add(conv)
            await db.flush()
            for m in msgs:
                db.add(Message(
                    conversation_id=conv.id,
                    from_who=m.get("from_who", "mukul"),
                    text=m["text"],
                    ts=m.get("ts", "10:00"),
                    date_label=m.get("date_label", "today"),
                    status=m.get("status", "draft"),
                    is_read=m.get("status") in ("sent", "received"),
                    by_ai=m.get("by_ai", False),
                    by_mukul_real=m.get("by_mukul_real", False),
                    requires_approval=m.get("requires_approval", False),
                    created_at=datetime.utcnow(),
                ))

        await db.commit()
        logger.info("Seed data inserted successfully")


def _start_scheduler():
    """Start the APScheduler background job for CRM polling."""
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.interval import IntervalTrigger

        scheduler = AsyncIOScheduler()

        async def _poll_crm():
            async with AsyncSessionLocal() as db:
                from app.api import crm as crm_api
                from app.api import checkin as checkin_api
                # We call the sync endpoint logic directly
                from fastapi import Request
                logger.info("CRM auto-poll: starting sync…")
                try:
                    # Auto-sync: comments last 48h, check-ins last 7 days
                    # Deduplication in sync functions ensures already-processed
                    # records are skipped automatically — no double processing.
                    result = await crm_api.sync_crm_comments(hours_back=48, days_back=None, emp_code=None, db=db)
                    new_comments = result.data.get("new_comments", 0) if result.data else 0
                    
                    checkin_result = await checkin_api.sync_checkin_data(days=7, db=db)
                    new_checkins = checkin_result.data.get("total_new", 0) if checkin_result.data else 0
                    
                    logger.info(f"CRM auto-sync completed: {new_comments} new comments, {new_checkins} new check-ins")
                    
                    # Process new comments
                    if new_comments > 0:
                        await crm_api.process_all_pending(db=db)
                except Exception as exc:
                    logger.error("CRM poll error: %s", exc)

        scheduler.add_job(
            _poll_crm,
            trigger=IntervalTrigger(minutes=settings.CRM_POLL_INTERVAL_MINUTES),
            id="crm_poll",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("CRM poll scheduler started (every %d min)", settings.CRM_POLL_INTERVAL_MINUTES)
    except Exception as exc:
        logger.warning("Scheduler not started: %s", exc)


# ─────────────────────────────────────────────────────────
#  APP
# ─────────────────────────────────────────────────────────
app = FastAPI(
    title="Hi-Tech AI Sales Org",
    description="AI-powered sales org management for Hi-Tech International Group",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins (Railway serves frontend from same domain via FileResponse,
# but external tools / WhatsApp webhooks need open CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(conversations.router)
app.include_router(whatsapp.router)
app.include_router(crm.router)
app.include_router(gmail.router)
app.include_router(settings_api.router)
app.include_router(dashboard.router)
app.include_router(checkin.router)
app.include_router(rep_dashboard.router)

# Import and include reps router
from app.api import reps
app.include_router(reps.router)

# Import and include knowledge base router
from app.api import knowledge_base
app.include_router(knowledge_base.router)


# ─────────────────────────────────────────────────────────
#  FRONTEND (serve index.html for all non-API routes)
# ─────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def serve_frontend():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"error": "Frontend not found. Place index.html in the /frontend directory."}


@app.get("/{path:path}", include_in_schema=False)
async def catch_all(path: str):
    if path.startswith("api/"):
        from fastapi import HTTPException
        raise HTTPException(404, "API endpoint not found")
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"error": "Frontend not found"}

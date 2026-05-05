"""
Check-in/Check-out service for tracking sales rep visits
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import CheckIn, Rep

logger = logging.getLogger(__name__)


async def sync_checkin_data(db: AsyncSession, days: int = 182) -> Dict:
    """
    Sync check-in data from CRM using the admin account (Nagender, emp_code=1494).
    ONE single CRM call returns all reps' check-in data — no per-rep looping.

    Args:
        db: Database session
        days: Number of days to sync (default 182 = 6 months)

    Returns:
        Summary of sync operation
    """
    from app.services import crm_client

    today = datetime.now()
    from_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")

    logger.info("Fetching ALL check-in data via admin (emp=%s) from %s to %s",
                settings.CRM_ADMIN_EMP_CODE, from_date, to_date)
    checkins = await crm_client.get_checkin_data(
        emp_code=None, from_date=from_date, to_date=to_date
    )

    total_fetched = len(checkins)
    total_new = 0
    total_updated = 0
    errors = []

    logger.info("Fetched %d check-in records from CRM", total_fetched)

    BATCH = 500
    for idx, checkin_data in enumerate(checkins):
        try:
            crm_id_raw = checkin_data.get("ID") or checkin_data.get("Id")
            crm_id = int(crm_id_raw) if crm_id_raw else None

            emp_code = str(checkin_data.get("EmpCode") or checkin_data.get("empCode") or "")
            if not emp_code or emp_code == "0":
                continue

            emp_name  = checkin_data.get("EMP_NAME") or checkin_data.get("empName") or ""
            comp_code_raw = checkin_data.get("CompCode") or checkin_data.get("compCode") or ""
            comp_code = str(comp_code_raw) if str(comp_code_raw) not in ("0", "") else None
            comp_name = checkin_data.get("COMP_NAME") or checkin_data.get("compName") or None

            ts_str = (
                checkin_data.get("CreatedonApp") or checkin_data.get("createdonApp") or
                checkin_data.get("Createdon")    or checkin_data.get("createdon")
            )
            if not ts_str:
                continue
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00").replace("+00:00+00:00", "+00:00"))
            checkin_date = dt.strftime("%d-%m-%Y")
            checkin_time = dt.strftime("%H:%M:%S")

            latitude  = checkin_data.get("Latitude")  or checkin_data.get("latitude")
            longitude = checkin_data.get("Longitude") or checkin_data.get("longitude")
            address   = (
                checkin_data.get("CompAddress") or checkin_data.get("compAddress") or
                checkin_data.get("Location")    or checkin_data.get("location") or None
            )

            # ── Primary dedup: CRM ID ─────────────────────────────────────────
            if crm_id:
                existing = await db.execute(
                    select(CheckIn).where(CheckIn.crm_id == crm_id)
                )
                existing_record = existing.scalar_one_or_none()
            else:
                # Fallback: emp + date + time
                existing = await db.execute(
                    select(CheckIn).where(
                        and_(
                            CheckIn.emp_code    == emp_code,
                            CheckIn.checkin_date == checkin_date,
                            CheckIn.checkin_time == checkin_time,
                        )
                    )
                )
                existing_record = existing.scalar_one_or_none()

            if existing_record:
                # Update mutable fields
                existing_record.crm_id     = crm_id or existing_record.crm_id
                existing_record.comp_code  = comp_code
                existing_record.comp_name  = comp_name
                existing_record.latitude   = str(latitude)  if latitude  else None
                existing_record.longitude  = str(longitude) if longitude else None
                existing_record.address    = address
                existing_record.updated_at = datetime.utcnow()
                total_updated += 1
            else:
                db.add(CheckIn(
                    crm_id=crm_id,
                    emp_code=emp_code,
                    emp_name=emp_name,
                    comp_code=comp_code,
                    comp_name=comp_name,
                    checkin_date=checkin_date,
                    checkin_time=checkin_time,
                    checkout_time=None,
                    duration_minutes=None,
                    latitude=str(latitude)  if latitude  else None,
                    longitude=str(longitude) if longitude else None,
                    address=address,
                    remarks=None,
                ))
                total_new += 1

        except Exception as e:
            errors.append(str(e))
            logger.error("Error processing check-in record: %s", e)

        # Commit in batches to avoid memory issues with large syncs
        if (idx + 1) % BATCH == 0:
            await db.commit()
            logger.info("Check-in batch committed: %d processed so far", idx + 1)

    await db.commit()
    
    return {
        "total_fetched": total_fetched,
        "total_new": total_new,
        "total_updated": total_updated,
        "errors": errors,
        "from_date": from_date,
        "to_date": to_date
    }


async def get_checkin_data(
    db: AsyncSession,
    emp_code: str,
    days: int = 7,
) -> List[CheckIn]:
    """
    Get check-in/check-out data for a sales rep from database.
    
    Args:
        db: Database session
        emp_code: Employee code
        days: Number of days to fetch
    
    Returns:
        List of check-in records
    """
    today = datetime.now()
    from_date = (today - timedelta(days=days)).strftime("%d-%m-%Y")
    
    result = await db.execute(
        select(CheckIn)
        .where(CheckIn.emp_code == emp_code)
        .where(CheckIn.checkin_date >= from_date)
        .order_by(CheckIn.checkin_date.desc(), CheckIn.checkin_time.desc())
    )
    
    return result.scalars().all()


async def analyze_visit_patterns(db: AsyncSession, emp_code: str, days: int = 7) -> Dict:
    """
    Analyze visit patterns for a sales rep from database.
    
    Args:
        db: Database session
        emp_code: Employee code
        days: Number of days to analyze
    
    Returns:
        Analysis of visit patterns
    """
    checkins = await get_checkin_data(db, emp_code, days)
    
    if not checkins:
        return {
            "total_visits": 0,
            "avg_duration_minutes": 0,
            "no_checkout": 0,
            "short_visits": 0,
            "long_visits": 0,
            "visits_by_day": {},
            "anomalies": []
        }
    
    total_visits = len(checkins)
    no_checkout = 0
    short_visits = 0
    long_visits = 0
    total_duration = 0
    visits_with_duration = 0
    visits_by_day = {}
    anomalies = []
    
    for visit in checkins:
        # Count visits by day
        if visit.checkin_date:
            visits_by_day[visit.checkin_date] = visits_by_day.get(visit.checkin_date, 0) + 1
        
        # Check for no checkout
        if not visit.checkout_time:
            no_checkout += 1
            anomalies.append({
                "type": "no_checkout",
                "customer": visit.comp_name or "Unknown",
                "date": visit.checkin_date,
                "checkin": visit.checkin_time
            })
            continue
        
        # Analyze duration
        if visit.duration_minutes:
            total_duration += visit.duration_minutes
            visits_with_duration += 1
            
            # Check for short visits
            if visit.duration_minutes < 10:
                short_visits += 1
                anomalies.append({
                    "type": "short_visit",
                    "customer": visit.comp_name or "Unknown",
                    "date": visit.checkin_date,
                    "duration": f"{visit.duration_minutes} min"
                })
            
            # Check for long visits
            elif visit.duration_minutes > 120:
                long_visits += 1
                anomalies.append({
                    "type": "long_visit",
                    "customer": visit.comp_name or "Unknown",
                    "date": visit.checkin_date,
                    "duration": f"{visit.duration_minutes} min"
                })
    
    avg_duration = total_duration / visits_with_duration if visits_with_duration > 0 else 0
    
    return {
        "total_visits": total_visits,
        "avg_duration_minutes": round(avg_duration, 1),
        "no_checkout": no_checkout,
        "short_visits": short_visits,
        "long_visits": long_visits,
        "visits_by_day": visits_by_day,
        "anomalies": anomalies[:10]  # Return top 10 anomalies
    }


async def get_team_visit_summary(db: AsyncSession, days: int = 7) -> Dict:
    """
    Get visit summary for entire team from database.
    
    Args:
        db: Database session
        days: Number of days to analyze
    
    Returns:
        Team-wide visit statistics
    """
    # Get all active reps
    result = await db.execute(
        select(Rep).where(Rep.is_active == True)
    )
    reps = result.scalars().all()
    
    team_stats = {
        "total_visits": 0,
        "total_reps": len(reps),
        "avg_visits_per_rep": 0,
        "reps_with_anomalies": 0,
        "top_performers": [],
        "needs_attention": []
    }
    
    rep_stats = []
    
    for rep in reps:
        if not rep.emp_code:
            continue
        
        analysis = await analyze_visit_patterns(db, rep.emp_code, days)
        
        if analysis["total_visits"] > 0:
            team_stats["total_visits"] += analysis["total_visits"]
            
            rep_stats.append({
                "emp_code": rep.emp_code,
                "name": rep.name,
                "visits": analysis["total_visits"],
                "avg_duration": analysis["avg_duration_minutes"],
                "anomalies": len(analysis["anomalies"])
            })
            
            if analysis["anomalies"]:
                team_stats["reps_with_anomalies"] += 1
    
    # Calculate averages
    if rep_stats:
        team_stats["avg_visits_per_rep"] = round(
            team_stats["total_visits"] / len(rep_stats), 1
        )
        
        # Sort by visits
        rep_stats.sort(key=lambda x: x["visits"], reverse=True)
        team_stats["top_performers"] = rep_stats[:5]
        
        # Find reps needing attention (low visits or many anomalies)
        needs_attention = [
            r for r in rep_stats 
            if r["visits"] < 3 or r["anomalies"] > 3
        ]
        team_stats["needs_attention"] = needs_attention[:5]
    
    return team_stats

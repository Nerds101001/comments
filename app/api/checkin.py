"""
Check-in/Check-out API endpoints
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Rep, CheckIn
from app.services import checkin_service
from app.schemas import StatusResponse

router = APIRouter(prefix="/api/checkin", tags=["checkin"])


@router.post("/sync", response_model=StatusResponse)
async def sync_checkin_data(
    days: int = Query(182, ge=1, le=365, description="Number of days to sync (default 182 = 6 months)"),
    db: AsyncSession = Depends(get_db),
):
    """Sync check-in/check-out data from CRM for all active reps."""
    from app.models import AppSetting
    from datetime import datetime
    
    result = await checkin_service.sync_checkin_data(db, days)
    
    # Update last check-in sync time
    now = datetime.utcnow()
    last_checkin_sync_result = await db.execute(
        select(AppSetting).where(AppSetting.key == "last_checkin_sync")
    )
    last_checkin_sync_setting = last_checkin_sync_result.scalar_one_or_none()
    
    if last_checkin_sync_setting:
        last_checkin_sync_setting.value = now.isoformat() + "Z"
        last_checkin_sync_setting.updated_at = now
    else:
        last_checkin_sync_setting = AppSetting(
            key="last_checkin_sync",
            value=now.isoformat() + "Z",
            updated_at=now
        )
        db.add(last_checkin_sync_setting)
    
    await db.commit()
    
    return StatusResponse(
        status="success",
        message=f"Synced {result['total_new']} new and {result['total_updated']} updated check-ins",
        data=result
    )


@router.get("/rep/{emp_code}")
async def get_rep_checkin_data(
    emp_code: str,
    days: int = Query(7, ge=1, le=30, description="Number of days to fetch"),
    db: AsyncSession = Depends(get_db),
):
    """Get check-in/check-out data for a specific rep from database."""
    checkins = await checkin_service.get_checkin_data(db, emp_code, days)
    
    today = datetime.now()
    from_date = (today - timedelta(days=days)).strftime("%d-%m-%Y")
    to_date = today.strftime("%d-%m-%Y")
    
    return {
        "emp_code": emp_code,
        "from_date": from_date,
        "to_date": to_date,
        "total_visits": len(checkins),
        "visits": [
            {
                "comp_code": c.comp_code,
                "comp_name": c.comp_name,
                "checkin_date": c.checkin_date,
                "checkin_time": c.checkin_time,
                "checkout_time": c.checkout_time,
                "duration_minutes": c.duration_minutes,
                "address": c.address,
                "remarks": c.remarks,
            }
            for c in checkins
        ]
    }


@router.get("/rep/{emp_code}/analysis")
async def get_rep_visit_analysis(
    emp_code: str,
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """Get visit pattern analysis for a specific rep from database."""
    # Get rep details
    result = await db.execute(
        select(Rep).where(Rep.emp_code == emp_code)
    )
    rep = result.scalar_one_or_none()
    
    if not rep:
        return {
            "error": "Rep not found",
            "emp_code": emp_code
        }
    
    analysis = await checkin_service.analyze_visit_patterns(db, emp_code, days)
    
    return {
        "emp_code": emp_code,
        "rep_name": rep.name,
        "days_analyzed": days,
        "analysis": analysis
    }


@router.get("/team/summary")
async def get_team_visit_summary(
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """Get visit summary for entire team from database."""
    summary = await checkin_service.get_team_visit_summary(db, days)
    
    return {
        "days_analyzed": days,
        "summary": summary
    }


@router.get("/anomalies")
async def get_visit_anomalies(
    days: int = Query(7, ge=1, le=30, description="Number of days to check"),
    db: AsyncSession = Depends(get_db),
):
    """Get all visit anomalies (no checkout, short visits, etc.) from database."""
    # Get all active reps
    result = await db.execute(
        select(Rep).where(Rep.is_active == True)
    )
    reps = result.scalars().all()
    
    all_anomalies = []
    
    for rep in reps:
        if not rep.emp_code:
            continue
        
        analysis = await checkin_service.analyze_visit_patterns(db, rep.emp_code, days)
        
        if analysis["anomalies"]:
            for anomaly in analysis["anomalies"]:
                all_anomalies.append({
                    "rep_name": rep.name,
                    "emp_code": rep.emp_code,
                    **anomaly
                })
    
    # Sort by date (most recent first)
    all_anomalies.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    return {
        "days_analyzed": days,
        "total_anomalies": len(all_anomalies),
        "anomalies": all_anomalies[:50]  # Return top 50
    }


@router.get("/stats")
async def get_checkin_stats(db: AsyncSession = Depends(get_db)):
    """Get overall check-in statistics from database."""
    # Count total check-ins
    result = await db.execute(select(CheckIn))
    all_checkins = result.scalars().all()
    
    # Count unique reps
    unique_reps = len(set(c.emp_code for c in all_checkins))
    
    # Count unique customers
    unique_customers = len(set(c.comp_code for c in all_checkins if c.comp_code))
    
    # Get date range
    dates = [c.checkin_date for c in all_checkins if c.checkin_date]
    min_date = min(dates) if dates else None
    max_date = max(dates) if dates else None
    
    return {
        "total_checkins": len(all_checkins),
        "unique_reps": unique_reps,
        "unique_customers": unique_customers,
        "date_range": {
            "from": min_date,
            "to": max_date
        }
    }

"""
CRM Client for rustx.net (https://api-crm.rustx.net)

Key endpoints used by this system:
  POST /api/Authentication/dologin                           — get/refresh Bearer token
  GET  /api/Comment/GetPipelineComment/{from}/{to}/{empCode} — pipeline comments by date+rep
  GET  /api/Comment/GetCommentByCustomerId/{Id}              — comments for a customer
  GET  /api/Comment/GetCompRecentComments/{Id}               — recent comments for a company
  GET  /api/Reports/GetCustomersLastComment/{empCode}        — last comment per customer per rep
  POST /api/Reports/GetCheckinData                           — check-in data report
  GET  /api/Customer/customerCheckInDetail/{CompCode}        — check-in details for a customer
  POST /api/Customer/GetCustomerList                         — customer list for a rep
  GET  /api/Dashboard/DashboardHeader/{empCode}              — rep dashboard stats
"""
from __future__ import annotations
import logging
from datetime import datetime, timedelta
from typing import Optional, List

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

CRM_BASE = settings.CRM_BASE_URL
_token_cache: dict = {"token": "", "expires_at": datetime.min}


# ─────────────────────────────────────────────────────────
#  AUTH  (auto-refresh token)
# ─────────────────────────────────────────────────────────
async def _get_token() -> str:
    """Return a valid Bearer token, refreshing if expired."""
    global _token_cache

    # Use statically configured token if no credentials set
    if settings.CRM_TOKEN and not settings.CRM_USERNAME:
        return settings.CRM_TOKEN

    # Refresh if about to expire (5-min buffer)
    if _token_cache["token"] and datetime.utcnow() < (_token_cache["expires_at"] - timedelta(minutes=5)):
        return _token_cache["token"]

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{CRM_BASE}/api/Authentication/dologin",
            headers={"Content-Type": "application/json"},
            json={"username": settings.CRM_USERNAME, "password": settings.CRM_PASSWORD},
        )
        resp.raise_for_status()
        data = resp.json()
        token = data.get("token") or data.get("Token") or data.get("TokenKey") or data.get("access_token", "")
        if not token:
            raise RuntimeError(f"CRM login failed: {data}")
        _token_cache = {
            "token": token,
            "expires_at": datetime.utcnow() + timedelta(hours=8),
        }
        logger.info("CRM token refreshed")
        return token


def _headers_sync(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


async def _get(path: str, params: dict = None) -> dict | list:
    token = await _get_token()
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            f"{CRM_BASE}{path}",
            headers=_headers_sync(token),
            params=params,
        )
        resp.raise_for_status()
        return resp.json()


async def _post(path: str, body: dict = None) -> dict | list:
    token = await _get_token()
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            f"{CRM_BASE}{path}",
            headers=_headers_sync(token),
            json=body or {},
        )
        resp.raise_for_status()
        return resp.json()


# ─────────────────────────────────────────────────────────
#  COMMENTS
# ─────────────────────────────────────────────────────────
async def get_pipeline_comments(
    emp_code: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
) -> list:
    """
    GET /api/Comment/GetPipelineComment/{fromDate}/{toDate}/{empCode}
    Fetch all pipeline comments for a rep between two dates.
    Dates in format: YYYY-MM-DD or DD-MM-YYYY (match CRM format).
    """
    today = datetime.utcnow()
    fd = from_date or (today - timedelta(days=1)).strftime("%d-%m-%Y")
    td = to_date or today.strftime("%d-%m-%Y")
    try:
        data = await _get(f"/api/Comment/GetPipelineComment/{fd}/{td}/{emp_code}")
        if isinstance(data, list): return data
        res = data.get("data") or data.get("Data") or data.get("Result")
        return res if isinstance(res, list) else []
    except Exception as exc:
        logger.error("get_pipeline_comments failed for emp %s: %s", emp_code, exc)
        return []


async def get_comments_by_customer(comp_code: str) -> list:
    """GET /api/Comment/GetCommentByCustomerId/{Id}"""
    try:
        data = await _get(f"/api/Comment/GetCommentByCustomerId/{comp_code}")
        if isinstance(data, list): return data
        res = data.get("data") or data.get("Data") or data.get("Result")
        return res if isinstance(res, list) else []
    except Exception as exc:
        logger.error("get_comments_by_customer failed for %s: %s", comp_code, exc)
        return []


async def get_recent_comments(comp_code: str) -> list:
    """GET /api/Comment/GetCompRecentComments/{Id}"""
    try:
        data = await _get(f"/api/Comment/GetCompRecentComments/{comp_code}")
        if isinstance(data, list): return data
        res = data.get("data") or data.get("Data") or data.get("Result")
        return res if isinstance(res, list) else []
    except Exception as exc:
        logger.error("get_recent_comments failed for %s: %s", comp_code, exc)
        return []


async def get_customers_last_comment(emp_code: str) -> list:
    """
    GET /api/Reports/GetCustomersLastComment/{empCode}
    Returns each customer's most recent comment for this rep.
    Perfect for the daily AI processing loop.
    
    Response format:
    {
        "Data": [
            {
                "COMP_CODE": 55205,
                "EMP_CODE": 1714,
                "Designation": "NEW BIZ",
                "EMP_NAME": "Sonia Arora",
                "COMP_NAME": "Coorg Organics Pvt LTd",
                "CITY": "Bengaluru",
                "STATE": "Karnataka",
                "Comment": "discussion is going on",
                "CreatedOn": "04/30/2026 13:49:47"
            },
            ...
        ],
        "StatusMessage": "Data has been fetched successfully",
        "StatusCode": 200,
        "Result": 1
    }
    """
    try:
        data = await _get(f"/api/Reports/GetCustomersLastComment/{emp_code}")
        if isinstance(data, list): 
            return data
        # The Data field contains the list of comments
        res = data.get("Data")
        if res is None:
            res = data.get("data") or data.get("Result")
        return res if isinstance(res, list) else []
    except Exception as exc:
        logger.error("get_customers_last_comment failed for %s: %s", emp_code, exc)
        return []


# ─────────────────────────────────────────────────────────
#  CHECK-IN DATA
# ─────────────────────────────────────────────────────────
async def get_checkin_data(
    emp_code: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
) -> list:
    """
    POST /api/Reports/GetCheckinData
    Returns check-in/check-out records with visit duration.
    """
    today = datetime.utcnow()
    body = {
        "fromDate": from_date or (today - timedelta(days=1)).strftime("%d-%m-%Y"),
        "toDate": to_date or today.strftime("%d-%m-%Y"),
    }
    if emp_code:
        body["empCode"] = emp_code
    try:
        data = await _post("/api/Reports/GetCheckinData", body)
        if isinstance(data, list): return data
        res = data.get("data") or data.get("Data") or data.get("Result")
        return res if isinstance(res, list) else []
    except Exception as exc:
        logger.error("get_checkin_data failed: %s", exc)
        return []


async def get_customer_checkin_detail(comp_code: str) -> dict:
    """GET /api/Customer/customerCheckInDetail/{CompCode}"""
    try:
        return await _get(f"/api/Customer/customerCheckInDetail/{comp_code}")
    except Exception as exc:
        logger.error("get_customer_checkin_detail failed for %s: %s", comp_code, exc)
        return {}


# ─────────────────────────────────────────────────────────
#  CUSTOMER LIST
# ─────────────────────────────────────────────────────────
async def get_customer_list(emp_code: Optional[str] = None) -> list:
    """POST /api/Customer/GetCustomerList"""
    body = {}
    if emp_code:
        body["empCode"] = emp_code
    try:
        data = await _post("/api/Customer/GetCustomerList", body)
        if isinstance(data, list): return data
        res = data.get("data") or data.get("Data") or data.get("Result")
        return res if isinstance(res, list) else []
    except Exception as exc:
        logger.error("get_customer_list failed: %s", exc)
        return []


async def get_company_by_id(comp_id: str) -> dict:
    """GET /api/Customer/getCompanyById/{id}"""
    try:
        return await _get(f"/api/Customer/getCompanyById/{comp_id}")
    except Exception as exc:
        logger.error("get_company_by_id failed for %s: %s", comp_id, exc)
        return {}


# ─────────────────────────────────────────────────────────
#  DASHBOARD HEADER (per rep stats)
# ─────────────────────────────────────────────────────────
async def get_rep_dashboard(emp_code: str) -> dict:
    """GET /api/Dashboard/DashboardHeader/{empCode}"""
    try:
        return await _get(f"/api/Dashboard/DashboardHeader/{emp_code}")
    except Exception as exc:
        logger.error("get_rep_dashboard failed for %s: %s", emp_code, exc)
        return {}


# ─────────────────────────────────────────────────────────
#  COMMENTS REPORT  (all reps, date range)
# ─────────────────────────────────────────────────────────
async def get_comments_report(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    emp_code: Optional[str] = None,
) -> list:
    """POST /api/Reports/GetCommentsReport"""
    today = datetime.utcnow()
    body = {
        "fromDate": from_date or (today - timedelta(days=1)).strftime("%d-%m-%Y"),
        "toDate":   to_date or today.strftime("%d-%m-%Y"),
    }
    if emp_code:
        body["empCode"] = emp_code
    try:
        data = await _post("/api/Reports/GetCommentsReport", body)
        if isinstance(data, list): return data
        res = data.get("data") or data.get("Data") or data.get("Result")
        return res if isinstance(res, list) else []
    except Exception as exc:
        logger.error("get_comments_report failed: %s", exc)
        return []


# ─────────────────────────────────────────────────────────
#  TEST CONNECTION
# ─────────────────────────────────────────────────────────
async def test_connection() -> dict:
    """Try to authenticate and return status."""
    try:
        token = await _get_token()
        return {"connected": True, "token_preview": token[:12] + "..."}
    except Exception as exc:
        return {"connected": False, "error": str(exc)}

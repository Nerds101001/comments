"""
Simple password-based authentication for the Hi-Tech AI Sales app.

- Single password protects the entire frontend
- Uses a signed session cookie (itsdangerous)
- Password stored as env var APP_PASSWORD (default: Rustx@3100)
- Login page served at /login
- All non-API routes redirect to /login if not authenticated
"""
from __future__ import annotations
import hashlib
import hmac
import time
import logging
from typing import Optional

from fastapi import APIRouter, Request, Response, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

# ── Config ────────────────────────────────────────────────────────────────────
APP_PASSWORD = getattr(settings, "APP_PASSWORD", "Rustx@3100")
COOKIE_NAME  = "hitech_session"
COOKIE_MAX_AGE = 60 * 60 * 3  # 3 hours


def _sign(value: str) -> str:
    """Create HMAC signature for cookie value."""
    return hmac.new(
        settings.APP_SECRET_KEY.encode(),
        value.encode(),
        hashlib.sha256,
    ).hexdigest()


def _make_cookie_value() -> str:
    ts = str(int(time.time()))
    sig = _sign(ts)
    return f"{ts}.{sig}"


def _verify_cookie(value: str) -> bool:
    try:
        ts, sig = value.rsplit(".", 1)
        expected = _sign(ts)
        if not hmac.compare_digest(sig, expected):
            return False
        # Expire after 7 days
        if time.time() - int(ts) > COOKIE_MAX_AGE:
            return False
        return True
    except Exception:
        return False


def is_authenticated(request: Request) -> bool:
    cookie = request.cookies.get(COOKIE_NAME, "")
    return _verify_cookie(cookie)


# ── Login page HTML ───────────────────────────────────────────────────────────
LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hi-Tech AI Sales · Login</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #0a0a0f;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }
  .card {
    background: #16161e;
    border: 1px solid #2a2a3a;
    border-radius: 16px;
    padding: 40px 36px;
    width: 100%;
    max-width: 380px;
    box-shadow: 0 24px 64px rgba(0,0,0,.5);
  }
  .logo {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 32px;
  }
  .logo-icon {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #007AFF, #5856D6);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
  }
  .logo-text h1 { font-size: 18px; font-weight: 700; color: #fff; }
  .logo-text p  { font-size: 12px; color: #666; margin-top: 2px; }
  label { display: block; font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 8px; }
  input[type=password] {
    width: 100%;
    padding: 12px 14px;
    background: #0d0d14;
    border: 1px solid #2a2a3a;
    border-radius: 10px;
    color: #fff;
    font-size: 15px;
    outline: none;
    transition: border-color .2s;
  }
  input[type=password]:focus { border-color: #007AFF; }
  button {
    width: 100%;
    margin-top: 20px;
    padding: 13px;
    background: #007AFF;
    color: #fff;
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: background .2s;
  }
  button:hover { background: #0066dd; }
  .error {
    margin-top: 16px;
    padding: 10px 14px;
    background: #2d1515;
    border: 1px solid #5c2020;
    border-radius: 8px;
    color: #ff6b6b;
    font-size: 13px;
    text-align: center;
  }
  .footer { margin-top: 28px; text-align: center; font-size: 12px; color: #444; }
</style>
</head>
<body>
<div class="card">
  <div class="logo">
    <div class="logo-icon">◆</div>
    <div class="logo-text">
      <h1>Hi-Tech AI Sales</h1>
      <p>Sales Organisation · Live</p>
    </div>
  </div>
  <form method="post" action="/login">
    <label for="pwd">Password</label>
    <input type="password" id="pwd" name="password" placeholder="Enter password" autofocus autocomplete="current-password">
    <button type="submit">Sign in</button>
    {error}
  </form>
  <div class="footer">Hi-Tech International Group · Confidential</div>
</div>
</body>
</html>"""


# ── Routes ────────────────────────────────────────────────────────────────────
@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse("/", status_code=302)
    return HTMLResponse(LOGIN_HTML.replace("{error}", ""))


@router.post("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_submit(request: Request, response: Response, password: str = Form(...)):
    if password == APP_PASSWORD:
        redirect = RedirectResponse("/", status_code=302)
        redirect.set_cookie(
            key=COOKIE_NAME,
            value=_make_cookie_value(),
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            samesite="lax",
            secure=not settings.DEBUG,  # HTTPS only in production
        )
        return redirect
    return HTMLResponse(
        LOGIN_HTML.replace("{error}", '<div class="error">Incorrect password. Try again.</div>'),
        status_code=401,
    )


@router.get("/logout", include_in_schema=False)
async def logout():
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie(COOKIE_NAME)
    return response

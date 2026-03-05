"""Auth routes.

Yahoo: OAuth2 authorization code flow — entirely server-side.
  GET  /auth/login         → redirect to Yahoo
  GET  /auth/callback      → exchange code, set session cookie, redirect to /
  POST /auth/espn-login    → validate ESPN cookies, set session cookie
  POST /auth/logout        → clear session
"""
import os
import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from httpx import HTTPStatusError
from pydantic import BaseModel

from yahoo_client import exchange_code
from espn_client import validate_and_get_leagues
from session import set_session, delete_session

router = APIRouter()

_YAHOO_AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
_SCOPE = "fspt-r"


@router.get("/auth/login")
def login():
    state = secrets.token_urlsafe(16)
    params = urlencode({
        "client_id": os.environ["YAHOO_CONSUMER_KEY"],
        "redirect_uri": os.environ["YAHOO_REDIRECT_URI"],
        "response_type": "code",
        "scope": _SCOPE,
        "state": state,
    })
    resp = RedirectResponse(url=f"{_YAHOO_AUTH_URL}?{params}")
    resp.set_cookie("oauth_state", state, httponly=True, samesite="lax", max_age=600, secure=True)
    return resp


@router.get("/auth/callback")
async def callback(code: str, state: str = "", oauth_state: str = Cookie(default="")):
    # State mismatch is a CSRF signal — reject silently with a redirect to /
    if state and oauth_state and state != oauth_state:
        return RedirectResponse(url="/")

    try:
        tokens = await exchange_code(code)
    except HTTPStatusError:
        # Code already consumed (duplicate callback request) — session was set by
        # the first request, so just redirect home without crashing.
        return RedirectResponse(url="/")

    session_id = secrets.token_urlsafe(32)
    set_session(session_id, tokens)

    resp = RedirectResponse(url="/")
    resp.set_cookie(
        "session_id", session_id,
        httponly=True, samesite="lax", max_age=86400, secure=True,
    )
    resp.delete_cookie("oauth_state")
    return resp


class EspnLoginRequest(BaseModel):
    espn_s2: str
    swid: str


@router.post("/auth/espn-login")
async def espn_login(body: EspnLoginRequest):
    """Accept ESPN browser cookies, validate them, create a session."""
    try:
        await validate_and_get_leagues(body.espn_s2, body.swid)
    except HTTPStatusError:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid ESPN cookies — please check and try again"},
        )

    session_id = secrets.token_urlsafe(32)
    set_session(session_id, {
        "provider": "espn",
        "espn_s2": body.espn_s2,
        "swid": body.swid,
    })

    resp = JSONResponse(content={"ok": True})
    resp.set_cookie(
        "session_id", session_id,
        httponly=True, samesite="lax", max_age=86400, secure=True,
    )
    return resp


@router.get("/api/session")
def session_info(session_id: str = Cookie(default=None)):
    """Return provider info for the current session (no sensitive data)."""
    from session import get_session as _get_session
    from fastapi import HTTPException
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tokens = _get_session(session_id)
    if not tokens:
        raise HTTPException(status_code=401, detail="Session expired")
    return {"provider": tokens.get("provider", "yahoo")}


@router.post("/auth/logout")
def logout(session_id: str = Cookie(default=None)):
    if session_id:
        delete_session(session_id)
    resp = Response(content="", status_code=204)
    resp.delete_cookie("session_id")
    return resp

"""Yahoo OAuth2 authorization code flow — entirely server-side.

Routes:
  GET  /auth/login    → redirect to Yahoo
  GET  /auth/callback → exchange code, set session cookie, redirect to /
  POST /auth/logout   → clear session
"""
import os
import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, Request
from fastapi.responses import RedirectResponse, Response
from httpx import HTTPStatusError

from yahoo_client import exchange_code
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


@router.post("/auth/logout")
def logout(session_id: str = Cookie(default=None)):
    if session_id:
        delete_session(session_id)
    resp = Response(content="", status_code=204)
    resp.delete_cookie("session_id")
    return resp

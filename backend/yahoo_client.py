"""Raw httpx calls for Yahoo OAuth2 token exchange and refresh.

Yahoo OAuth2 endpoints:
  Authorization: https://api.login.yahoo.com/oauth2/request_auth
  Token:         https://api.login.yahoo.com/oauth2/get_token
"""
import os
import time
import base64
import httpx

_TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"


def _basic_auth() -> str:
    key = os.environ["YAHOO_CONSUMER_KEY"]
    secret = os.environ["YAHOO_CONSUMER_SECRET"]
    return base64.b64encode(f"{key}:{secret}".encode()).decode()


async def exchange_code(code: str) -> dict:
    """Exchange an authorization code for access + refresh tokens.

    Returns the token dict as-is from Yahoo, augmented with token_time.
    """
    redirect_uri = os.environ["YAHOO_REDIRECT_URI"]
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            _TOKEN_URL,
            headers={
                "Authorization": f"Basic {_basic_auth()}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
        )
        resp.raise_for_status()
        tokens = resp.json()
        tokens["token_time"] = time.time()
        return tokens


async def refresh_access_token(refresh_token: str) -> dict:
    """Use a refresh token to obtain a new access token.

    Returns the new token dict augmented with token_time.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            _TOKEN_URL,
            headers={
                "Authorization": f"Basic {_basic_auth()}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )
        resp.raise_for_status()
        tokens = resp.json()
        tokens["token_time"] = time.time()
        return tokens


def is_token_expired(tokens: dict, buffer_seconds: int = 60) -> bool:
    """Return True if the access token has expired (or will expire within buffer_seconds)."""
    issued_at = float(tokens.get("token_time", 0))
    expires_in = int(tokens.get("expires_in", 3600))
    return time.time() >= issued_at + expires_in - buffer_seconds

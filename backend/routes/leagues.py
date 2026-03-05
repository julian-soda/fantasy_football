"""GET /api/leagues — list the authenticated user's Fantasy NFL leagues.

Supports Yahoo (OAuth) and ESPN (browser cookies).
"""
import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException
from session import get_session, refresh_session
from yahoo_client import is_token_expired, refresh_access_token
from espn_client import validate_and_get_leagues

router = APIRouter()

_YAHOO_LEAGUES_URL = (
    "https://fantasysports.yahooapis.com/fantasy/v2"
    "/users;use_login=1/games;game_codes=nfl/leagues"
    "?format=json"
)


async def _get_tokens(session_id: str = Cookie(default=None)) -> dict:
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tokens = get_session(session_id)
    if not tokens:
        raise HTTPException(status_code=401, detail="Session expired — please log in again")

    # Only refresh OAuth tokens for Yahoo sessions
    if tokens.get("provider", "yahoo") == "yahoo" and is_token_expired(tokens):
        new_tokens = await refresh_access_token(tokens["refresh_token"])
        refresh_session(session_id, new_tokens)
        tokens = get_session(session_id)

    return tokens


@router.get("/leagues")
async def list_leagues(tokens: dict = Depends(_get_tokens)):
    """Return a list of the user's NFL Fantasy leagues across all seasons."""
    provider = tokens.get("provider", "yahoo")

    if provider == "espn":
        try:
            leagues = await validate_and_get_leagues(tokens["espn_s2"], tokens["swid"])
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=401, detail="ESPN cookies are invalid — please log in again")
        leagues.sort(key=lambda x: x["year"], reverse=True)
        return leagues

    # Yahoo
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            _YAHOO_LEAGUES_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        if resp.status_code == 401:
            raise HTTPException(status_code=401, detail="Yahoo token rejected — please log in again")
        resp.raise_for_status()

    data = resp.json()

    leagues = []
    try:
        games = (
            data["fantasy_content"]["users"]["0"]["user"][1]["games"]
        )
        game_count = int(games["count"])
        for gi in range(game_count):
            game = games[str(gi)]["game"]
            season = int(game[0]["season"])
            raw_leagues = game[1]["leagues"]
            league_count = int(raw_leagues["count"])
            for li in range(league_count):
                league = raw_leagues[str(li)]["league"][0]
                leagues.append({
                    "league_id": league["league_id"],
                    "name": league["name"],
                    "year": season,
                    "num_teams": int(league.get("num_teams", 0)),
                })
    except (KeyError, TypeError, IndexError):
        # Return empty list rather than 500 if Yahoo's schema changes
        pass

    # Sort newest season first
    leagues.sort(key=lambda x: x["year"], reverse=True)
    return leagues

"""GET /api/leagues — list the authenticated user's Yahoo Fantasy NFL leagues."""
import asyncio
import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException
from session import get_session
from yahoo_client import is_token_expired, refresh_access_token
from session import refresh_session

router = APIRouter()

# Step 1: fetch all NFL game keys for the user (no /leagues sub-resource —
# that combined form returns 403 with current Yahoo API restrictions).
_USER_GAMES_URL = (
    "https://fantasysports.yahooapis.com/fantasy/v2"
    "/users;use_login=1/games;game_codes=nfl"
    "?format=json"
)

# Step 2: fetch leagues for one specific game key.
# Using game_keys= (per-key) instead of game_codes=nfl/leagues (combined)
# matches what yfpy does and avoids the 403.
_USER_LEAGUES_URL = (
    "https://fantasysports.yahooapis.com/fantasy/v2"
    "/users;use_login=1/games;game_keys={game_key}/leagues"
    "?format=json"
)


async def _get_tokens(session_id: str = Cookie(default=None)) -> dict:
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tokens = get_session(session_id)
    if not tokens:
        raise HTTPException(status_code=401, detail="Session expired — please log in again")

    # Proactively refresh if the access token is about to expire
    if is_token_expired(tokens):
        new_tokens = await refresh_access_token(tokens["refresh_token"])
        refresh_session(session_id, new_tokens)
        tokens = get_session(session_id)

    return tokens


@router.get("/leagues")
async def list_leagues(tokens: dict = Depends(_get_tokens)):
    """Return a list of the user's NFL Fantasy leagues across all seasons."""
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    async with httpx.AsyncClient() as client:
        # Step 1: get all NFL game keys for this user
        resp = await client.get(_USER_GAMES_URL, headers=headers)
        if resp.status_code == 401:
            raise HTTPException(status_code=401, detail="Yahoo token rejected — please log in again")
        if not resp.is_success:
            raise HTTPException(status_code=502, detail="Yahoo Fantasy API unavailable")

        game_keys = []
        try:
            games = resp.json()["fantasy_content"]["users"]["0"]["user"][1]["games"]
            for gi in range(int(games["count"])):
                game_keys.append(games[str(gi)]["game"][0]["game_key"])
        except (KeyError, TypeError, IndexError):
            return []

        if not game_keys:
            return []

        # Step 2: fetch leagues for each game key concurrently
        async def fetch_for_game(game_key: str):
            r = await client.get(
                _USER_LEAGUES_URL.format(game_key=game_key), headers=headers
            )
            if not r.is_success:
                return []
            try:
                game = r.json()["fantasy_content"]["users"]["0"]["user"][1]["games"]["0"]["game"]
                season = int(game[0]["season"])
                raw_leagues = game[1]["leagues"]
                result = []
                for li in range(int(raw_leagues["count"])):
                    league = raw_leagues[str(li)]["league"][0]
                    result.append({
                        "league_id": league["league_id"],
                        "name": league["name"],
                        "year": season,
                        "num_teams": int(league.get("num_teams", 0)),
                    })
                return result
            except (KeyError, TypeError, IndexError):
                return []

        results = await asyncio.gather(*[fetch_for_game(k) for k in game_keys])

    leagues = [league for game_leagues in results for league in game_leagues]
    leagues.sort(key=lambda x: x["year"], reverse=True)
    return leagues

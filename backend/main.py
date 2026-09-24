"""FastAPI application entry point."""
import httpx
from fastapi import FastAPI, Cookie
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from routes.leagues import router as leagues_router
from routes.calculate import router as calculate_router
from routes.results import router as results_router
from session import get_session

app = FastAPI(title="FF Luck Calculator API")

# CORS is largely handled by Vercel's proxy rewrites, but allow all origins
# here to support local development against the backend directly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(leagues_router, prefix="/api")
app.include_router(calculate_router, prefix="/api")
app.include_router(results_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/debug")
async def debug(session_id: str = Cookie(default=None)):
    """Temporary endpoint: test Yahoo API access at multiple levels."""
    results = {}

    # Test 1: unauthenticated public game metadata
    async with httpx.AsyncClient() as client:
        r = await client.get("https://fantasysports.yahooapis.com/fantasy/v2/game/nfl?format=json")
        results["public_game_endpoint"] = {"status": r.status_code, "body": r.text[:300]}

    # Test 2: authenticated user endpoint (requires valid session)
    if session_id:
        tokens = get_session(session_id)
        if tokens:
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    "https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1?format=json",
                    headers=headers,
                )
                results["user_endpoint"] = {"status": r.status_code, "body": r.text[:300]}
                r2 = await client.get(
                    "https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;codes=nfl?format=json",
                    headers=headers,
                )
                results["user_games_endpoint"] = {"status": r2.status_code, "body": r2.text[:300]}
        else:
            results["session"] = "invalid or expired"
    else:
        results["session"] = "no session cookie"

    return results

"""GET /api/calculate — SSE streaming endpoint for the luck calculation.

The calculation is CPU-bound and takes 2–3 minutes for a 10-team, 14-week
season. It runs in a background thread so it does not block the async event
loop. Progress events are sent to the browser one per team via Server-Sent
Events as soon as each team's simulation finishes.

Query params:
  league_id   (required) Yahoo league ID
  year        (required) Season year, e.g. 2024
  through_week (optional) Only include data through this week number
"""
import asyncio
import json
import queue
import sys
import threading
from pathlib import Path

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

# Shared auth helper — imported from leagues to avoid duplication
from routes.leagues import _get_tokens
from routes.results import save_result

# Add the app root to sys.path so ff_luck and yahoo_api are importable
# (__file__ is .../routes/calculate.py → .parent.parent is the app root)
sys.path.insert(0, str(Path(__file__).parent.parent))
from ff_luck import simulate_all_teams
from yahoo_api import fetch_stats

router = APIRouter()


@router.get("/calculate")
async def calculate(
    league_id: str = Query(...),
    year: int = Query(...),
    through_week: int = Query(default=None),
    tokens: dict = Depends(_get_tokens),
):
    """Stream per-team luck results as SSE events."""
    loop = asyncio.get_event_loop()
    q: queue.Queue = queue.Queue()

    def run():
        try:
            stats = fetch_stats(
                league_id, year,
                access_token_json=tokens,
                through_week=through_week,
            )
            for team, luck_index, pct_worse, pct_better in simulate_all_teams(stats):
                q.put({
                    "type": "progress",
                    "team": team,
                    "luck_index": round(luck_index, 2),
                    "pct_worse": round(pct_worse, 2),
                    "pct_better": round(pct_better, 2),
                    "record": stats[team]["record"],
                    "scores": stats[team]["scores"],
                })
            q.put(None)  # sentinel: calculation finished normally
        except Exception as exc:
            q.put({"type": "error", "message": str(exc)})
            q.put(None)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    async def event_stream():
        results = []
        while True:
            event = await loop.run_in_executor(None, q.get)
            if event is None:
                break
            yield f"data: {json.dumps(event)}\n\n"
            if event.get("type") == "progress":
                results.append(event)
            elif event.get("type") == "error":
                return

        if results:
            result_id = save_result(league_id, year, through_week, results)
            yield f"data: {json.dumps({'type': 'complete', 'result_id': result_id})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )

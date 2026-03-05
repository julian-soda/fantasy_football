# CLAUDE.md

## Project
Fantasy football luck analyzer. Fetches live data from the Yahoo Fantasy Sports API
and computes a luck index for each team by simulating every possible schedule permutation.

## Key files (CLI)
- `ff_luck.py` — CLI entry point and simulation/output logic
- `yahoo_api.py` — Yahoo API integration (`fetch_stats`)
- `test_ff_luck.py` — unit, integration, and regression tests

## Webapp
The project also has a full-stack web app:

**Backend** (`backend/`) — FastAPI, deployed on AWS App Runner
- `main.py`, `auth.py`, `session.py`, `yahoo_client.py`
- `routes/leagues.py`, `routes/calculate.py`, `routes/results.py`
- Docker build context is `fantasy_football/` dir: `docker build -f backend/Dockerfile .`
- DynamoDB tables: `ff-sessions` (TTL=24h), `ff-results` (public)
- Env vars: `YAHOO_CONSUMER_KEY`, `YAHOO_CONSUMER_SECRET`, `YAHOO_REDIRECT_URI`, `SESSION_COOKIE_SECRET`, `AWS_DEFAULT_REGION`

**Frontend** (`frontend/`) — React + Vite, deployed on Vercel
- Components: `LuckTable.tsx`, `LuckBarChart.tsx`, `DistributionChart.tsx`, `WeeklyScoresChart.tsx`
- Pages: `Results.tsx`, others
- Hooks: `src/hooks/useIsMobile.ts` (640px breakpoint, uses `window.matchMedia`)
- Uses inline React styles throughout (no CSS modules or Tailwind)
- Update `frontend/vercel.json` with the App Runner URL before deploying

**CI/CD**: `.github/workflows/deploy-backend.yml` and `deploy-frontend.yml`

## Known gotchas
- Yahoo OAuth callback can fire twice (browser double-request). `auth.py` catches the resulting 400 from Yahoo and redirects home — the session from the first request is already valid.
- Recharts `XAxis`: `angle` and `textAnchor` are top-level props on `<XAxis>`, not inside the `tick` object.

## Running
```
make run LEAGUE_ID=<id> YEAR=<year>                      # full season
make run LEAGUE_ID=<id> YEAR=<year> THROUGH_WEEK=8       # mid-season snapshot
make test
```

## Testing
Tests are purely synthetic/local — no API calls. The regression tests use a
hardcoded 2024 season stats dict in `test_ff_luck.py` (not fetched from Yahoo).
All 28 tests should pass without credentials.

## Credentials
Copy `.env.template` → `.env` and fill in Yahoo API keys. `.env` is gitignored.
The first `make run` will open a browser for OAuth; tokens are saved back to `.env`.

## Development workflow
When updating `ff_luck.py`, always check whether corresponding updates are needed
in the Makefile, README, and tests. Ask if unsure whether something is appropriate.

## Conventions
- `fetch_stats` returns `{ team_name: { 'scores': [...], 'record': 'W-L-T' } }`
- Records are derived from matchup scores directly, not from Yahoo standings
- Scores are always in week order

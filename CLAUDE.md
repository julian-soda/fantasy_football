# CLAUDE.md

## Project
Fantasy football luck analyzer. Fetches live data from the Yahoo Fantasy Sports API
and computes a luck index for each team by simulating every possible schedule permutation.

## Key files
- `ff_luck.py` — CLI entry point and simulation/output logic
- `yahoo_api.py` — Yahoo API integration (`fetch_stats`)
- `test_ff_luck.py` — unit, integration, and regression tests

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

## Webapp

### Structure
- `backend/` — FastAPI app: `main.py`, `auth.py`, `session.py`, `yahoo_client.py`, `routes/`
- `frontend/` — React + Vite app: `src/pages/`, `src/components/`, `src/hooks/`

### Infrastructure
- Backend: AWS App Runner (prod service: `ff-luck-api`)
- Frontend: Vercel (rewrites `/api/*` and `/auth/*` to App Runner URL via `vercel.json`)
- Image registry: ECR repo `ff-luck-backend`
- DynamoDB tables: `ff-sessions` (TTL 24h), `ff-results` (permanent, public)

### Running locally
```
cd backend && uvicorn main:app --reload   # needs env vars below
cd frontend && npm run dev
```

### Required env vars (backend)
- `YAHOO_CONSUMER_KEY`, `YAHOO_CONSUMER_SECRET`, `YAHOO_REDIRECT_URI`
- `SESSION_COOKIE_SECRET`
- `AWS_DEFAULT_REGION`
- `SESSIONS_TABLE` (default: `ff-sessions`), `RESULTS_TABLE` (default: `ff-results`)

### Deployment
Push to master triggers:
- `deploy-backend.yml` — builds Docker image, pushes to ECR, deploys to App Runner
- `deploy-frontend.yml` — deploys to Vercel (`--prod`)

Docker build context is the `fantasy_football/` directory:
```
docker build -f backend/Dockerfile .
```

### Key conventions
- Sessions stored in DynamoDB with 24h TTL; `session_id` is an HttpOnly cookie
- Results cached by `provider#league_id#year#through_week` key in `ff-results` table
- Calculation streams SSE events (one per team) then a final `complete` event with `result_id`
- `/results/:id` is publicly readable (no auth required) for shareable links

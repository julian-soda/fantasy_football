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

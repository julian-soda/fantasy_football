"""ESPN cookie validation and league discovery.

ESPN uses browser session cookies (espn_s2 + SWID) rather than OAuth.
No developer account or registration required.
"""
import httpx

_ESPN_USER_LEAGUES_URL = (
    "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}"
    "?view=userSettings"
)

_ESPN_SEASONS = list(range(2024, 2014, -1))  # 2024 down to 2015


async def validate_and_get_leagues(espn_s2: str, swid: str) -> list[dict]:
    """Validate ESPN cookies by fetching the user's leagues.

    Returns a list of league dicts: {league_id, name, year, num_teams}
    Raises httpx.HTTPStatusError if cookies are invalid.
    Raises ValueError if no leagues found (cookies may be valid but user has no leagues).
    """
    cookies = {"espn_s2": espn_s2, "SWID": swid}
    leagues = []

    async with httpx.AsyncClient() as client:
        for year in _ESPN_SEASONS:
            url = _ESPN_USER_LEAGUES_URL.format(year=year)
            resp = await client.get(url, cookies=cookies)
            if resp.status_code == 401:
                raise httpx.HTTPStatusError(
                    "ESPN cookies are invalid or expired",
                    request=resp.request,
                    response=resp,
                )
            if not resp.is_success:
                continue

            data = resp.json()
            # userSettings contains the user's league memberships for this season
            try:
                preferences = data.get("preferences", [])
                for pref in preferences:
                    meta = pref.get("metaData", {})
                    entry_data = pref.get("entryData", {})
                    # League membership entries have type "ffl"
                    if meta.get("type") != "ffl":
                        continue
                    league_id = str(meta.get("leagueId") or entry_data.get("leagueId", ""))
                    name = entry_data.get("leagueName", f"ESPN League {league_id}")
                    size = int(entry_data.get("leagueSize", 0))
                    if league_id:
                        leagues.append({
                            "league_id": league_id,
                            "name": name,
                            "year": year,
                            "num_teams": size,
                        })
            except (KeyError, TypeError, AttributeError):
                continue

    # Deduplicate by (league_id, year)
    seen = set()
    unique = []
    for lg in leagues:
        key = (lg["league_id"], lg["year"])
        if key not in seen:
            seen.add(key)
            unique.append(lg)

    return unique

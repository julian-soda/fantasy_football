"""ESPN Fantasy Football data fetcher.

Returns the same format as yahoo_api.fetch_stats:
  { team_name: { 'scores': [...], 'record': 'W-L-T' } }

Uses the espn-api PyPI library (pip install espn-api).
No developer account required — ESPN uses browser session cookies.
"""
from espn_api.football import League


def fetch_stats(league_id, year, espn_s2, swid, through_week=None):
    """Fetch weekly scores and records for all teams in an ESPN league.

    Args:
        league_id:    ESPN league ID (int or str)
        year:         Season year (e.g. 2024)
        espn_s2:      espn_s2 cookie value from espn.com
        swid:         SWID cookie value from espn.com (format: {GUID})
        through_week: Only include data through this week number (optional)

    Returns:
        dict mapping team name → { 'scores': [...], 'record': 'W-L-T' }
    """
    league = League(
        league_id=int(league_id),
        year=int(year),
        espn_s2=espn_s2,
        swid=swid,
    )

    reg_season_weeks = league.settings.reg_season_count
    max_week = min(through_week, reg_season_weeks) if through_week else reg_season_weeks

    stats = {}
    for team in league.teams:
        scores = list(team.scores[:max_week])

        wins = losses = ties = 0
        for i, opp in enumerate(team.schedule[:max_week]):
            my_score = team.scores[i]
            opp_score = opp.scores[i]
            if my_score > opp_score:
                wins += 1
            elif my_score < opp_score:
                losses += 1
            else:
                ties += 1

        stats[team.team_name] = {
            'scores': scores,
            'record': f'{wins}-{losses}-{ties}',
        }

    return stats

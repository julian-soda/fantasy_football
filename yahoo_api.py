from pathlib import Path
from yfpy.query import YahooFantasySportsQuery


def fetch_stats(league_id: str, year: int, env_file: str = '.env') -> dict:
    """Fetch team scores and records for the regular season from Yahoo Fantasy.

    Returns a stats dict in the same format used by ff_luck.py:
        { team_name: { 'scores': [...], 'record': 'W-L-T' }, ... }

    Records and scores cover the regular season only (playoff weeks excluded).
    """
    env_path = Path(env_file)

    # First query (no game_id) is used only to resolve the year → game_id.
    # This works because get_game_key_by_season queries Yahoo's games endpoint,
    # which doesn't require a specific league/season context.
    resolver = YahooFantasySportsQuery(
        league_id=league_id,
        game_code='nfl',
        env_file_location=env_path,
        save_token_data_to_env_file=True,
    )
    game_id = int(resolver.get_game_key_by_season(year))

    query = YahooFantasySportsQuery(
        league_id=league_id,
        game_code='nfl',
        game_id=game_id,
        env_file_location=env_path,
        save_token_data_to_env_file=True,
    )

    # Determine how many regular season weeks to fetch
    settings = query.get_league_settings()
    num_regular_season_weeks = settings.playoff_start_week - 1

    # Initialise per-team accumulators
    teams = query.get_league_teams()
    stats = {
        team.name: {'scores': [], 'wins': 0, 'losses': 0, 'ties': 0}
        for team in teams
    }

    # Fetch each regular season week
    for week in range(1, num_regular_season_weeks + 1):
        scoreboard = query.get_league_scoreboard_by_week(week)
        for matchup in scoreboard.matchups:
            team_a, team_b = matchup.teams[0], matchup.teams[1]
            stats[team_a.name]['scores'].append(team_a.points)
            stats[team_b.name]['scores'].append(team_b.points)
            if team_a.points > team_b.points:
                stats[team_a.name]['wins'] += 1
                stats[team_b.name]['losses'] += 1
            elif team_b.points > team_a.points:
                stats[team_b.name]['wins'] += 1
                stats[team_a.name]['losses'] += 1
            else:
                stats[team_a.name]['ties'] += 1
                stats[team_b.name]['ties'] += 1

    # Collapse counters into a record string and clean up
    for team in stats:
        w = stats[team].pop('wins')
        l = stats[team].pop('losses')
        t = stats[team].pop('ties')
        stats[team]['record'] = f'{w}-{l}-{t}'

    return stats

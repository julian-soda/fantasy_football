from pathlib import Path
from dotenv import load_dotenv
from yfpy.query import YahooFantasySportsQuery


def fetch_stats(league_id: str, year: int, env_file: str = '.env', through_week: int = None) -> dict:
    """Fetch team scores and records for the regular season from Yahoo Fantasy.

    Returns a stats dict in the same format used by ff_luck.py:
        { team_name: { 'scores': [...], 'record': 'W-L-T' }, ... }

    Records and scores cover the regular season only (playoff weeks excluded).
    If through_week is specified, only weeks 1 through through_week are included.
    """
    env_path = Path(env_file)
    load_dotenv(env_path)
    env_dir = env_path.parent  # yfpy expects the directory containing .env, not the file itself

    # First query (no game_id) is used only to resolve the year → game_id.
    # This works because get_game_key_by_season queries Yahoo's games endpoint,
    # which doesn't require a specific league/season context.
    resolver = YahooFantasySportsQuery(
        league_id=league_id,
        game_code='nfl',
        env_file_location=env_dir,
        save_token_data_to_env_file=True,
    )
    game_id = int(resolver.get_game_key_by_season(year))

    query = YahooFantasySportsQuery(
        league_id=league_id,
        game_code='nfl',
        game_id=game_id,
        env_file_location=env_dir,
        save_token_data_to_env_file=True,
    )

    # Determine how many regular season weeks to fetch
    settings = query.get_league_settings()
    num_regular_season_weeks = settings.playoff_start_week - 1
    if through_week is not None:
        num_regular_season_weeks = min(num_regular_season_weeks, through_week)

    def team_name(t):
        name = t.name.decode('utf-8') if isinstance(t.name, bytes) else t.name
        return name.encode('ascii', errors='ignore').decode('ascii')

    # Initialise per-team accumulators keyed by team_id for reliable lookup
    teams = query.get_league_teams()
    league_key = query.get_league_key()
    team_id_to_name = {team.team_id: team_name(team) for team in teams}
    stats = {
        team_name(team): {'scores_by_week': {}, 'wins': 0, 'losses': 0, 'ties': 0}
        for team in teams
    }

    # Fetch matchups via the team endpoint, which works for both current and
    # archived seasons (unlike get_league_scoreboard_by_week, which fails for
    # completed seasons). Each team's matchup list covers their full season;
    # we filter to regular season weeks and deduplicate so each matchup is
    # only processed once.
    seen_matchups = set()  # (week, team_key_a, team_key_b) tuples
    for team in teams:
        name = team_name(team)
        team_key = f"{league_key}.t.{team.team_id}"
        for matchup in query.get_team_matchups(team.team_id):
            week_num = int(matchup.week)
            if int(matchup.is_playoffs) or week_num > num_regular_season_weeks:
                continue
            # Deduplicate: sort the two team keys so (A,B) and (B,A) map to the same key
            keys = tuple(sorted(t.team_key for t in matchup.teams))
            dedup_key = (week_num,) + keys
            if dedup_key in seen_matchups:
                continue
            seen_matchups.add(dedup_key)

            team_a, team_b = matchup.teams[0], matchup.teams[1]
            name_a = team_id_to_name.get(team_a.team_id, team_name(team_a))
            name_b = team_id_to_name.get(team_b.team_id, team_name(team_b))
            stats[name_a]['scores_by_week'][week_num] = team_a.points
            stats[name_b]['scores_by_week'][week_num] = team_b.points
            if team_a.points > team_b.points:
                stats[name_a]['wins'] += 1
                stats[name_b]['losses'] += 1
            elif team_b.points > team_a.points:
                stats[name_b]['wins'] += 1
                stats[name_a]['losses'] += 1
            else:
                stats[name_a]['ties'] += 1
                stats[name_b]['ties'] += 1

    # Convert scores_by_week dicts to week-ordered lists
    for name in stats:
        stats[name]['scores'] = [
            stats[name]['scores_by_week'][w]
            for w in sorted(stats[name]['scores_by_week'])
        ]
        del stats[name]['scores_by_week']

    # Collapse counters into a record string and clean up
    for team in stats:
        w = stats[team].pop('wins')
        l = stats[team].pop('losses')
        t = stats[team].pop('ties')
        stats[team]['record'] = f'{w}-{l}-{t}'

    return stats

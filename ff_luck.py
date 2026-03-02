#!/bin/env python3

import itertools
import math
from collections import defaultdict


def simulate_season(team_scores, opponent_scores_map, permutation, num_weeks, cycle_length):
    """Simulate a season with a specific opponent ordering.
    Returns (wins, losses, ties).
    """
    wins = losses = ties = 0
    for week in range(num_weeks):
        opponent = permutation[week % cycle_length]      # mod to implement schedule repeat
        opp_score = opponent_scores_map[opponent][week]
        if team_scores[week] > opp_score:
            wins += 1
        elif team_scores[week] < opp_score:
            losses += 1
        else:
            ties += 1
    return wins, losses, ties


def compute_luck(results, actual_record):
    """Given a results dict (record string -> count) and the team's actual record string,
    return (pct_worse, pct_better): the percentage of schedule permutations that produced
    a worse or better record than actual.
    """
    actual_wins = int(actual_record.split('-')[0])
    total = float(sum(results.values()))
    pct_worse = pct_better = 0.0
    for record, count in results.items():
        wins = int(record.split('-')[0])
        pct = count / total * 100.0
        if wins < actual_wins:
            pct_worse += pct
        elif wins > actual_wins:
            pct_better += pct
    return pct_worse, pct_better


def simulate_all_teams(stats: dict, debug: bool = False):
    """Simulate every possible schedule permutation for each team.
    Yields (team_name, luck_index, pct_worse, pct_better) per team.
    """
    weeks = max(len(x['scores']) for x in stats.values())
    team_count = len(stats)
    opponent_scores = {name: data['scores'] for name, data in stats.items()}
    perm_len = min(weeks, team_count - 1)
    perm_count = math.perm(team_count - 1, perm_len)

    for team in stats:
        results = defaultdict(int)
        if debug:
            print(f"Simulating {team} ({perm_count:,} permutations)...", flush=True)
        for i in itertools.permutations([a for a in stats.keys() if a != team], perm_len):
            wins, losses, ties = simulate_season(stats[team]['scores'], opponent_scores, i, weeks, team_count - 1)
            results[f"{wins}-{losses}-{ties}"] += 1

        pct_worse, pct_better = compute_luck(results, stats[team]['record'])
        yield team, pct_worse - pct_better, pct_worse, pct_better


if __name__ == '__main__':
    import argparse
    from yahoo_api import fetch_stats

    parser = argparse.ArgumentParser(description='Compute fantasy football luck index from Yahoo league data.')
    parser.add_argument('--league-id', required=True, help='Yahoo league ID')
    parser.add_argument('--year', type=int, required=True, help='Season year (e.g. 2024)')
    parser.add_argument('--through-week', type=int, default=None, help='Only include data through this week number')
    parser.add_argument('--debug', action='store_true', help='Print progress during fetch and simulation')
    args = parser.parse_args()

    stats = fetch_stats(args.league_id, args.year, through_week=args.through_week, debug=args.debug)

    max_team_len = max(len(x) for x in stats.keys()) + 5
    luck_index = {}

    for team, li, pct_worse, pct_better in simulate_all_teams(stats, debug=args.debug):
        luck_index[team] = li
        distance = abs(pct_worse - pct_better)
        direction = 'bad' if pct_better > pct_worse else 'good'
        adjective = {0: "average",
                     1: f"pretty {direction}",
                     2: f"very {direction}",
                     3: f"extremely {direction}"}.get(int(distance) // 25)
        print(f"  {team} - with a record of {stats[team]['record']},")
        print(f"    {pct_worse:.2f}% of all schedule combinations had the team with a worse record")
        print(f"    {pct_better:.2f}% of all schedule combinations had the team with a better record")
        print(f"  {adjective} luck")
        print()

    print("Luck index (most to least)")
    for place, team in enumerate(sorted(luck_index.items(), key=lambda x: x[1], reverse=True), start=1):
        print(f"{place:2}   {team[0]:{max_team_len}} {team[1]:.2f}")

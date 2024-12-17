#!/bin/env python3

import sys
import itertools
from collections import defaultdict

#                  week    1       2      3       4      5       6       7       8       9      10      11     12     13      14
stats = { 'reason will prevail': {
              'scores': [ 93.46, 93.52, 138.26, 92.44, 126.48, 104.02, 121.00, 125.90, 82.20, 130.70, 125.38, 99.66, 131.64, 160.42 ],
              'record': '10-4-0',
          },
          'bad ass boys': {
              'scores': [ 84.28, 97.16, 116.74, 70.30, 91.24, 94.90, 118.12, 87.22, 78.00, 104.40, 98.68, 116.82, 97.72, 125.58 ],
              'record': '4-10-0', 
          },
          'planters punch': {
              'scores': [ 113.58, 99.26, 72.48, 88.34, 116.06, 114.68, 95.08, 95.68, 141.32, 67.24, 109.94, 100.28, 104.02, 117.36 ],
              'record': '6-8-0',
          },
          'fillitupmoon': {
              'scores': [ 119.06, 126.00, 91.00, 114.80, 107.34, 119.38, 98.64, 123.84, 129.92, 110.88, 81.88, 108.48, 101.48, 130.34 ],
              'record': '10-4-0',
          },
          'i like the cure': {
              'scores': [ 101.44, 116.34, 96.98, 146.62, 116.52, 122.86, 75.94, 104.30, 89.06, 82.08, 104.34, 106.50, 116.04, 133.70 ],
              'record': '8-6-0',
          },
          'chris cornells crusaders': {
              'scores': [ 121.72, 113.42, 114.14, 118.00, 102.06, 118.86, 143.76, 122.34, 107.20, 94.68, 123.14, 122.26, 125.32, 121.92 ],
              'record': '6-8-0',
          },
          'flash them tds': {
              'scores': [ 122.42, 81.28, 91.18, 84.74, 120.12, 93.22, 112.64, 102.86, 60.70, 80.10, 65.08, 74.48, 82.18, 41.40 ],
              'record': '3-11-0',
          },
          'plate gate': {
              'scores': [ 104.86, 99.62, 144.66, 99.58, 124.58, 75.72, 100.84, 111.46, 131.64, 120.02, 107.84, 124.98, 131.06, 109.16 ],
              'record': '9-5-0',
          },
          'flip delaware': {
              'scores': [ 108.18, 124.10, 71.52, 115.88, 97.40, 111.10, 113.00, 128.80, 106.10, 91.64, 126.90, 91.06, 121.30, 104.00 ],
              'record': '8-6-0',
          },
          'gridiron onesies': {
              'scores': [ 75.18, 154.94, 86.78, 101.98, 128.50, 80.06, 92.80, 115.18, 109.66, 123.94, 104.18, 76.62, 92.58, 118.26 ],
              'record': '6-8-0',
          },
        }

weeks = max([ len(x['scores']) for x in stats.values() ])
max_team_len = max([ len(x) for x in stats.keys() ]) + 5

team_count = len(stats.keys())
luck_index = {}

for team in stats:
    results = defaultdict(lambda: 0)
    # the number of permutations we need is the minimum of the # of weeks so far and the number of opponents
    # in yahooo and espn, the schedule just repeats (in a 10 team league, you play the same team weeks 1 and 10
    for i in itertools.permutations( [ a for a in stats.keys() if a != team ], min(weeks,team_count-1) ):
        (wins, losses, ties) = (0,0,0)
        for week in range(weeks):
            opponent = i[week % (team_count - 1)]      # mod to implement schedule repeat
            if stats[team]['scores'][week] > stats[opponent]['scores'][week]:
                wins += 1
            elif stats[team]['scores'][week] < stats[opponent]['scores'][week]:
                losses += 1
            else:
                ties += 1
        record = f"{wins}-{losses}-{ties}"
        results[record] += 1

    total = float(sum(results.values()))
    (above,below) = (0.0,0.0)
    for r in sorted(results,key=lambda x: int(x.split('-')[0])):
        star = '*' if r == stats[team]['record'] else ' '
        print(f"{team:{max_team_len}} {star}: {r:6} - {results[r]:6} - {float(results[r]) / total * 100.0:.2f}%")
        if int(r.split('-')[0]) < int(stats[team]['record'].split('-')[0]):
            above += float(results[r]) / total * 100.0
        elif int(r.split('-')[0]) > int(stats[team]['record'].split('-')[0]):
            below += float(results[r]) / total * 100.0
    distance = abs(above - below)
    luck_index[team] = above - below
    direction = 'bad' if below > above else 'good'
    adjective = {0: "average",
                 1: f"pretty {direction}",
                 2: f"very {direction}",
                 3: f"extremely {direction}"}.get(int(distance) // 25)
    print(f"  {team} - with a record of {stats[team]['record']},")
    print(f"    {above:.2f}% of all schedule combinations had the team with a worse record")
    print(f"    {below:.2f}% of all schedule combinations had the team with a better record")
    print(f"  {adjective} luck")
    print()

print("Luck index (most to least)")
for place,team in enumerate(sorted(luck_index.items(),key=lambda x: x[1], reverse=True),start=1):
    print(f"{place:2}   {team[0]:{max_team_len}} {team[1]:.2f}")

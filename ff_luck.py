#!/bin/env python3

import sys
import itertools
from collections import defaultdict

#                  week      1       2       3       4       5       6       7       8      9    10      11     12     13     14
stats = { 'reason will prevail': {
              'scores': [ 126.14, 74.46, 131.26, 118.98, 113.82, 111.98, 151.54, 173.06, 98.82, 141.62, 100.8, 88.12, 131.3, 103.0 ],
              'record': '6-8-0',
          },
          'bad ass boys': {
              'scores': [ 65.24, 111.06, 126.22, 121.20, 139.06, 82.96, 104.10, 127.96, 91.82, 93.58, 107.7, 125.64, 106.78, 101.14 ],
              'record': '10-4-0', 
          },
          'rusty scuppers': {
              'scores': [ 131.36, 140.20, 138.80, 132.18, 63.92, 112.78, 94.26, 139.62, 101.64, 144.42, 108.6, 122.58, 70.38, 110.94 ],
              'record': '10-4-0',
          },
          'geos sad sacks': {
              'scores': [ 120.74, 111.44, 87.86, 110.58, 118.14, 110.54, 126.56, 99.48, 134.4, 91.44, 119.44, 137.06, 166.16, 73.04 ],
              'record': '8-6-0',
          },
          'clem fandango': {
              'scores': [ 93.16, 96.08, 101.88, 93.54, 121.24, 100.42, 100.58, 82.18, 81.38, 113.22, 125.56, 107.98, 98.44, 125.24 ],
              'record': '8-6-0',
          },
          'fairy quadmothers': {
              'scores': [ 105.96, 84.72, 113.22, 85.64, 70.58, 96.64, 100.5, 93.66, 109.5, 97.28, 71.14, 106.34, 67.5, 86.14,  ],
              'record': '3-11-0',
          },
          'flash them tds': {
              'scores': [ 97.90, 89.82, 138.28, 114.16, 98.52, 103.00, 86.26, 105.26, 73.28, 110.84, 109.7, 98.8, 82.02, 78.28 ],
              'record': '4-10-0',
          },
          'lets see paul allens team': {
              'scores': [ 56.38, 138.48, 118.42, 65.9, 128.38, 105.30, 112.06, 114.42, 117.02, 119.98, 102.74, 80.20, 126.52, 108.22 ],
              'record': '9-5-0',
          },
          'quadfathers': {
              'scores': [ 90.14, 124.80, 127.98, 123.42, 122.84, 54.74, 122.06, 90.4, 115.42, 83.66, 99.98, 116.22, 165.0, 103.54 ],
              'record': '5-9-0',
          },
          'dinkin flickas': {
              'scores': [ 110.14, 108.84, 123.56, 101.4, 127.18, 69.92, 53.8, 96.76, 103.26, 112.62, 81.24, 93.08, 75.08, 113.82 ],
              'record': '7-7-0',
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

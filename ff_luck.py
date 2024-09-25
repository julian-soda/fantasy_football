#!/bin/env python3

import sys
import itertools
from collections import defaultdict

#                  week      1       2       3       4       5       6       7       8      9    10      11     12     13     14
stats = { 'reason will prevail': {
              'scores': [ 93.46, 93.52, 138.26 ],
              'record': '1-2-0',
          },
          'bad ass boys': {
              'scores': [ 84.28, 97.16, 116.74 ],
              'record': '1-2-0', 
          },
          'no maxy boys': {
              'scores': [ 113.58, 99.26, 72.48 ],
              'record': '0-3-0',
          },
          'geos sad sacks': {
              'scores': [ 119.06, 126.00, 91.00 ],
              'record': '2-1-0',
          },
          'dave grohls conscience': {
              'scores': [ 101.44, 116.34, 96.98 ],
              'record': '3-0-0',
          },
          'hurts donut': {
              'scores': [ 121.72, 113.42, 114.14 ],
              'record': '2-1-0',
          },
          'flash them tds': {
              'scores': [ 122.42, 81.28, 91.18 ],
              'record': '2-1-0',
          },
          'lets see paul allens team': {
              'scores': [ 104.86, 99.62, 144.66 ],
              'record': '2-1-0',
          },
          'jake cave': {
              'scores': [ 108.18, 124.10, 71.52 ],
              'record': '1-2-0',
          },
          'rushin collusion': {
              'scores': [ 75.18, 154.94, 86.78 ],
              'record': '1-2-0',
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

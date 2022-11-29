#!/bin/env python3

import sys
import itertools
from collections import defaultdict

#                  week      1       2       3       4       5       6       7       8       9      10     11       12
stats = { 'reason will prevail': {
              'scores': [ 100.00, 124.46, 91.50,  110.34, 80.68,  112.08, 83.76,  141.62, 144.64, 145.58, 94.70,  100.06,  ],
              'record': '6-6-0',
          },
          'the closer': {
              'scores': [ 100.68, 100.48, 96.76,  72.56,  102.72, 101.02, 81.30,  89.60,  89.10,  103.12, 115.84, 99.24, ],
              'record': '4-8-0',
          },
          'planters punch': {
              'scores': [ 102.70, 104.06, 99.36,  111.08, 134.76, 102.32, 96.52,  111.76, 129.42, 140.18, 149.52, 103.32, ],
              'record': '9-3-0',
          },
          'geos sad sacks': {
              'scores': [ 128.88, 121.18, 123.80, 107.32, 123.56, 95.86,  98.34,  92.02,  120.20, 85.10,  74.08,  118.72,  ],
              'record': '7-5-0',
          },
          'i dont choose the way': {
              'scores': [ 116.22, 157.92, 110.62, 100.26, 102.66, 115.10, 120.90, 150.82, 101.62, 61.84,  117.16, 120.86, ],
              'record': '8-4-0',
          },
          'kirbys lacemakers': {
              'scores': [ 141.20, 127.80, 86.98,  81.56,  119.80, 100.82, 80.22,  102.24, 126.34, 131.14, 136.36, 107.14, ],
              'record': '5-7-0',
          },
          'wildcard bitches!':  {
              'scores': [ 104.32, 140.82, 88.70,  118.86, 174.96, 98.60,  96.90,  134.00, 91.12,  69.10,  122.70, 133.92, ],
              'record': '8-4-0',
          },
          'lets see paul allens card': {
              'scores': [ 102.22, 120.28, 75.76,  90.18,  116.50, 102.48, 110.06, 133.40, 95.80,  82.20,  71.10,  88.26,  ],
              'record': '3-9-0',
          },
          'who do you think you are i am':{
              'scores': [ 104.02, 117.56, 105.00, 152.18, 121.18, 91.70,  158.44, 133.58, 87.26,  81.50,  122.30, 111.40, ],
              'record': '4-8-0',
          },
          'dude looks like a brady':{
              'scores': [ 120.56, 109.56, 129.56, 148.30, 107.12, 56.02,  114.42, 103.98, 101.00, 94.70,  108.46, 106.46, ],
              'record': '6-6-0',
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

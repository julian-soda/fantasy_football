#!/bin/env python3

import sys
import itertools
from collections import defaultdict

#                  week      1       2       3       4       5       6       7       8       9      10      11
stats = { 'reason will prevail': {
              'scores': [ 100.00, 124.46, 91.50,  110.34, 80.68,  112.08, 83.76,  141.62, 144.64, 145.58, 94.70,  ],
              'record': 'XX',
          },
          'the closer': {
              'scores': [ 100.68, 100.48, 96.76,  72.56,  102.72, 101.02, 81.30,  89.60,  89.10,  103.12, 115.84, ],
              'record': 'XX',
          },
          'planters punch': {
              'scores': [ 102.70, 104.06, 99.36,  111.08, 134.76, 102.32, 96.52,  111.76, 129.42, 140.18, 149.52, ],
              'record': 'XX',
          },
          'geos sad sacks': {
              'scores': [ 128.88, 121.18, 123.80, 107.32, 123.56, 95.86,  98.34,  92.02,  120.20, 85.10,  74.08,  ],
              'record': 'XX',
          },
          'i dont choose the way': {
              'scores': [ 116.22, 157.92, 110.62, 100.26, 102.66, 115.10, 120.90, 150.82, 101.62, 61.84,  117.16, ],
              'record': 'XX',
          },
          'kirbys lacemakers': {
              'scores': [ 141.20, 127.80, 86.98,  81.56,  119.80, 100.82, 80.22,  102.24, 126.34, 131.14, 136.36, ],
              'record': 'XX',
          },
          'wildcard bitches!':  {
              'scores': [ 104.32, 140.82, 88.70,  118.86, 174.96, 98.60,  96.90,  134.00, 91.12,  69.10,  122.70, ],
              'record': 'XX',
          },
          'lets see paul allens card': {
              'scores': [ 102.22, 120.28, 75.76,  90.18,  116.50, 102.48, 110.06, 133.40, 95.80,  82.20,  71.10,  ],
              'record': 'XX',
          },
          'who do you think you are i am':{
              'scores': [ 104.02, 117.56, 105.00, 152.18, 121.18, 91.70,  158.44, 133.58, 87.26,  81.50,  122.30, ],
              'record': 'XX',
          },
          'dude looks like a brady':{
              'scores': [ 120.56, 109.56, 129.56, 148.30, 107.12, 56.02,  114.42, 103.98, 101.00, 94.70,  108.46, ],
              'record': 'XX',
          },
        }

weeks = max([ len(x['scores']) for x in stats.values() ])

team_count = len(stats.keys())

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
    for r in sorted(results,key=lambda x: int(x.split('-')[0])):
        print(f"{team:40} : {r:6} - {results[r]:6} - {float(results[r]) / total * 100.0:.2f}%")
    print()

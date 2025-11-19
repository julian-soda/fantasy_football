#!/bin/env python3

import sys
import itertools
from collections import defaultdict

#                  week    1       2      3       4      5       6       7       8       9      10      11     12     13      14
stats = { 'nabers think im sellin dope': {
              'scores': [ 85.78, 113.86, 117.88, 116.12, 112.52, 77.12, 129.14, 79.92, 127.46, 164.60, 95.90 ],
              'record': '7-4-0',
          },
          'reason will prevail': {
              'scores': [ 102.22, 100.38, 86.22, 153.38, 130.68, 118.26, 103.66, 138.40, 118.42, 66.64, 90.96 ],
              'record': '7-4-0', 
          },
          'the b-dubs council': {
              'scores': [ 113.82, 106.40, 103.72, 122.68, 89.84, 80.64, 100.94, 107.52, 133.32, 97.72, 108.60 ],
              'record': '6-5-0',
          },
          'tushpusherstm': {
              'scores': [ 77.72, 93.34, 100.62, 111.12, 128.10, 129.34, 92.48, 27.90, 114.94, 121.50, 101.34 ],
              'record': '6-5-0',
          },
          'fillitupmoon': {
              'scores': [ 70.94, 102.64, 151.92, 97.44, 121.68, 128.18, 150.16, 143.78, 95.12, 141.20, 100.50 ],
              'record': '5-6-0',
          },
          'zack baunongahela river': {
              'scores': [ 80.18, 110.24, 123.04, 119.30, 111.60, 104.92, 148.14, 82.36, 141.98, 91.62, 85.50 ],
              'record': '5-6-0',
          },
          'dynasty': {
              'scores': [ 106.56, 111.20, 59.72, 86.08, 105.74, 130.76, 117.40, 131.08, 128.50, 110.64, 96.72 ],
              'record': '5-6-0',
          },
          'chris cornells crusaders': {
              'scores': [ 94.08, 108.02, 88.02, 92.38, 98.96, 100.44, 83.02, 90.98, 95.80, 116.62, 105.32 ],
              'record': '5-6-0',
          },
          'its ridiculous': {
              'scores': [ 92.62, 109.38, 77.26, 105.30, 104.42, 77.58, 86.64, 112.96, 53.00, 116.18, 97.04 ],
              'record': '5-6-0',
          },
          'planters punch': {
              'scores': [ 136.76, 105.82, 85.92, 122.26, 84.42, 74.40, 118.42, 152.08, 93.28, 110.54, 164.08 ],
              'record': '4-7-0',
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

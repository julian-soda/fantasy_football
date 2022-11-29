# fantasy_football

Luck counts as much as skill in fantasy football - injuries, draft order, and - most of all -
the order in which you play against the teams in your league. Even if you have the second
most points in the league for a given week, if the team you play against has the most, 
that still counts as a loss, and you're still a loser.

This script aims to measure the impact of schedule order and determine the degree to which
your win/loss record can be attributed to luck. It does so by generating every possible
schedule order for each team, determines the count of win/loss totals based on the team's
and possible opponent's scores for each week, and compares the overall results to the teams' 
actual records.

Assumptions:
- applicable only to regular season - not playoffs
- each team plays every other team in the league (no subdivisions)
- once you've played each team, the order repeats; this is the way espn and yahoo leagues work
  to the best of my determination

## Luck Index

Luck Index is a score between 100 and -100 that measures the direction and amount of luck
in your win/loss record.  Positive scores indicate good luck, and negative scores indicate
bad luck.  Scores near 0 indicate very little luck, and scores near 100/-100 indicate extreme
amounts of luck. The score is based on the following formula:

```
sum of % of all schedule combinations where a team would have a worse record than actual
- 
sum of % of all schedule combinations where a team would have a better record than actual
```

For example, if 1.40% of all schedule combinations had the team with a worse record, and
92.47% of all schedule combinations had the team with a better record, that team would have
extremely bad schedule luck and would have a Luck Index score of -91.07.

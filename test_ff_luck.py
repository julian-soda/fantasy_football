import pytest
import itertools
from collections import defaultdict

from ff_luck import simulate_season, compute_luck

# ---------------------------------------------------------------------------
# Reference data (2024 season, hand-verified) used by regression tests
# ---------------------------------------------------------------------------
#                   week    1       2      3       4      5       6       7       8       9      10      11     12     13      14
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

team_count = len(stats)


# ---------------------------------------------------------------------------
# simulate_season
# ---------------------------------------------------------------------------

class TestSimulateSeason:
    def test_all_wins(self):
        team_scores = [100, 100, 100]
        opp_map = {'A': [80, 80, 80], 'B': [70, 70, 70]}
        assert simulate_season(team_scores, opp_map, ('A', 'B'), 3, 2) == (3, 0, 0)

    def test_all_losses(self):
        team_scores = [50, 50, 50]
        opp_map = {'A': [80, 80, 80], 'B': [70, 70, 70]}
        assert simulate_season(team_scores, opp_map, ('A', 'B'), 3, 2) == (0, 3, 0)

    def test_tie(self):
        # week 0: tie, week 1: loss, week 2: win
        team_scores = [100, 80, 60]
        opp_map = {'A': [100, 90, 50]}
        assert simulate_season(team_scores, opp_map, ('A',), 3, 1) == (1, 1, 1)

    def test_schedule_repeat(self):
        # 3 weeks, cycle_length=2: week 0 vs A, week 1 vs B, week 2 vs A again
        team_scores = [100, 50, 100]
        opp_map = {'A': [80, 80, 80], 'B': [60, 60, 60]}
        # week 0: 100 > 80 win, week 1: 50 < 60 loss, week 2: 100 > 80 win
        assert simulate_season(team_scores, opp_map, ('A', 'B'), 3, 2) == (2, 1, 0)

    def test_permutation_order_matters(self):
        # Swapping opponent order in a schedule with unequal scores should change the record
        team_scores = [100, 10]
        opp_map = {'strong': [90, 90], 'weak': [5, 5]}
        # vs strong then weak: win (100>90), win (10>5) -> 2-0-0
        assert simulate_season(team_scores, opp_map, ('strong', 'weak'), 2, 2) == (2, 0, 0)
        # vs weak then strong: win (100>5), loss (10<90) -> 1-1-0
        assert simulate_season(team_scores, opp_map, ('weak', 'strong'), 2, 2) == (1, 1, 0)


# ---------------------------------------------------------------------------
# compute_luck
# ---------------------------------------------------------------------------

class TestComputeLuck:
    def test_all_schedules_worse(self):
        results = {'3-0-0': 50, '4-0-0': 50}
        pct_worse, pct_better = compute_luck(results, '5-0-0')
        assert pct_worse == pytest.approx(100.0)
        assert pct_better == pytest.approx(0.0)

    def test_all_schedules_better(self):
        results = {'7-0-0': 50, '8-0-0': 50}
        pct_worse, pct_better = compute_luck(results, '5-0-0')
        assert pct_worse == pytest.approx(0.0)
        assert pct_better == pytest.approx(100.0)

    def test_split_evenly(self):
        results = {'3-0-0': 50, '7-0-0': 50}
        pct_worse, pct_better = compute_luck(results, '5-0-0')
        assert pct_worse == pytest.approx(50.0)
        assert pct_better == pytest.approx(50.0)

    def test_actual_record_excluded(self):
        # The actual record itself should not count toward either bucket
        results = {'3-0-0': 25, '5-0-0': 50, '7-0-0': 25}
        pct_worse, pct_better = compute_luck(results, '5-0-0')
        assert pct_worse == pytest.approx(25.0)
        assert pct_better == pytest.approx(25.0)

    def test_luck_index_sign(self):
        # More schedules worse than actual → positive luck index
        results = {'1-6-0': 70, '4-3-0': 30}
        pct_worse, pct_better = compute_luck(results, '3-4-0')
        assert pct_worse - pct_better > 0   # good luck

        # More schedules better than actual → negative luck index
        results2 = {'6-1-0': 70, '3-4-0': 30}
        pct_worse2, pct_better2 = compute_luck(results2, '4-3-0')
        assert pct_worse2 - pct_better2 < 0  # bad luck


# ---------------------------------------------------------------------------
# Small synthetic integration tests
# ---------------------------------------------------------------------------

def _run_simulation(team, all_stats):
    """Run the full permutation simulation for one team, return results dict."""
    num_teams = len(all_stats)
    num_weeks = max(len(v['scores']) for v in all_stats.values())
    cycle_length = num_teams - 1
    opp_scores = {name: data['scores'] for name, data in all_stats.items()}
    opponents = [a for a in all_stats if a != team]
    results = defaultdict(lambda: 0)
    for perm in itertools.permutations(opponents, min(num_weeks, cycle_length)):
        w, l, t = simulate_season(all_stats[team]['scores'], opp_scores, perm, num_weeks, cycle_length)
        results[f'{w}-{l}-{t}'] += 1
    return results

class TestIntegration:
    def test_dominant_team_always_wins(self):
        """A team that outscores every opponent every week has a perfect record in all permutations."""
        tiny = {
            'dominant': {'scores': [200, 200], 'record': '2-0-0'},
            'team_b':   {'scores': [ 50,  50], 'record': '0-2-0'},
            'team_c':   {'scores': [ 60,  60], 'record': '0-2-0'},
        }
        results = _run_simulation('dominant', tiny)
        assert set(results.keys()) == {'2-0-0'}
        assert sum(results.values()) == 2  # 2! permutations

    def test_dominant_team_luck_is_neutral(self):
        """A team that always wins has no luck — it would win under any schedule."""
        tiny = {
            'dominant': {'scores': [200, 200], 'record': '2-0-0'},
            'team_b':   {'scores': [ 50,  50], 'record': '0-2-0'},
            'team_c':   {'scores': [ 60,  60], 'record': '0-2-0'},
        }
        results = _run_simulation('dominant', tiny)
        pct_worse, pct_better = compute_luck(results, '2-0-0')
        assert pct_worse == pytest.approx(0.0)
        assert pct_better == pytest.approx(0.0)

    def test_worst_team_luck_is_neutral(self):
        """A team that always loses has no luck — it would lose under any schedule."""
        tiny = {
            'worst':  {'scores': [ 10,  10], 'record': '0-2-0'},
            'team_b': {'scores': [ 80,  80], 'record': '2-0-0'},
            'team_c': {'scores': [ 90,  90], 'record': '2-0-0'},
        }
        results = _run_simulation('worst', tiny)
        pct_worse, pct_better = compute_luck(results, '0-2-0')
        assert pct_worse == pytest.approx(0.0)
        assert pct_better == pytest.approx(0.0)

    def test_total_permutations_3_team(self):
        """3-team, 2-week season should produce exactly 2! = 2 permutations."""
        tiny = {
            'alpha': {'scores': [100, 60], 'record': '1-1-0'},
            'beta':  {'scores': [ 80, 70], 'record': '1-1-0'},
            'gamma': {'scores': [ 90, 50], 'record': '1-1-0'},
        }
        results = _run_simulation('alpha', tiny)
        assert sum(results.values()) == 2

    def test_schedule_sensitivity(self):
        """Verify that a team's record changes depending on opponent order."""
        # alpha beats beta but loses to gamma
        tiny = {
            'alpha': {'scores': [100, 100], 'record': '1-1-0'},
            'beta':  {'scores': [ 80,  80], 'record': '0-2-0'},
            'gamma': {'scores': [120, 120], 'record': '2-0-0'},
        }
        # 2 weeks, 2 opponents, cycle_length=2, no repeat needed
        opp_scores = {name: data['scores'] for name, data in tiny.items()}
        # perm (beta, gamma): week 0 vs beta win, week 1 vs gamma loss -> 1-1-0
        assert simulate_season([100, 100], opp_scores, ('beta', 'gamma'), 2, 2) == (1, 1, 0)
        # perm (gamma, beta): week 0 vs gamma loss, week 1 vs beta win -> 1-1-0
        assert simulate_season([100, 100], opp_scores, ('gamma', 'beta'), 2, 2) == (1, 1, 0)


# ---------------------------------------------------------------------------
# Regression tests against known output for the actual stats data
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def all_results():
    """Run the full simulation for every team. Slow (~30s) but shared across all tests."""
    return {team: _run_simulation(team, stats) for team in stats}

class TestRegression:
    def test_total_permutations(self, all_results):
        """Every team should have exactly 9! = 362,880 permutations."""
        import math
        expected = math.factorial(team_count - 1)
        for team, results in all_results.items():
            assert sum(results.values()) == expected, f"{team} permutation count wrong"

    @pytest.mark.parametrize('team,expected_index', [
        ('fillitupmoon',            63.81),
        ('reason will prevail',     50.80),
        ('flip delaware',           42.33),
        ('plate gate',              37.20),
        ('i like the cure',         25.82),
        ('planters punch',          16.99),
        ('gridiron onesies',        -5.28),
        ('flash them tds',         -20.53),
        ('bad ass boys',           -43.65),
        ('chris cornells crusaders',-97.50),
    ])
    def test_luck_index(self, all_results, team, expected_index):
        pct_worse, pct_better = compute_luck(all_results[team], stats[team]['record'])
        assert pct_worse - pct_better == pytest.approx(expected_index, abs=0.01)

    @pytest.mark.parametrize('team,expected_pct_worse,expected_pct_better', [
        ('reason will prevail',     62.28, 11.48),
        ('chris cornells crusaders',  0.38, 97.88),
    ])
    def test_pct_worse_and_better(self, all_results, team, expected_pct_worse, expected_pct_better):
        pct_worse, pct_better = compute_luck(all_results[team], stats[team]['record'])
        assert pct_worse  == pytest.approx(expected_pct_worse,  abs=0.01)
        assert pct_better == pytest.approx(expected_pct_better, abs=0.01)

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

## Setup

### Prerequisites

- Python 3.9+
- A Yahoo Fantasy Sports account with access to the league you want to analyze
- A Yahoo Developer application (free) to obtain API credentials

### 1. Get Yahoo API credentials

1. Go to the [Yahoo Developer Network](https://developer.yahoo.com/apps/) and create a new app.
2. Set the application type to **Installed Application**.
3. Under **API Permissions**, select **Fantasy Sports (Read)**.
4. Set the redirect URI to `https://localhost:8080`.
5. After creating the app, note your **Client ID** (Consumer Key) and **Client Secret** (Consumer Secret).

### 2. Configure credentials

Copy the template and fill in your credentials:

```
cp .env.template .env
```

Edit `.env`:

```
YAHOO_CONSUMER_KEY=your_client_id_here
YAHOO_CONSUMER_SECRET=your_client_secret_here
```

`.env` is gitignored and will never be committed.

### 3. Find your league ID

Your league ID is visible in the URL when you visit your league on Yahoo Fantasy:

```
https://football.fantasysports.yahoo.com/f1/XXXXXX
```

`XXXXXX` is your league ID.

### 4. Install dependencies

```
make test   # creates .venv and installs dependencies as a side effect
```

Or manually:

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Usage

```
make run LEAGUE_ID=<your_league_id> YEAR=<season_year>
```

Example:

```
make run LEAGUE_ID=123456 YEAR=2024
```

To analyze only through a specific week (useful mid-season):

```
make run LEAGUE_ID=123456 YEAR=2024 THROUGH_WEEK=8
```

**First run:** A browser window will open asking you to authorize the app with your Yahoo account.
Click **Allow**, then paste the verification code back into the terminal when prompted.
Your tokens will be saved to `.env` automatically — subsequent runs will not require browser authorization.

## Development

Run the test suite:

```
make test
```

Remove the virtual environment and caches:

```
make clean
```

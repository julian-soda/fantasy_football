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

---

## CLI Usage

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

### 5. Run

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

To print progress during fetching and simulation (useful for diagnosing slow runs):

```
make run LEAGUE_ID=123456 YEAR=2024 DEBUG=1
```

**First run:** A browser window will open asking you to authorize the app with your Yahoo account.
Click **Allow**, then paste the verification code back into the terminal when prompted.
Your tokens will be saved to `.env` automatically — subsequent runs will not require browser authorization.

### Development

Run the test suite:

```
make test
```

Remove the virtual environment and caches:

```
make clean
```

---

## Webapp Deployment

The webapp consists of:
- **Backend** — FastAPI on AWS App Runner (streams results via SSE)
- **Frontend** — React + Vite on Vercel
- **Storage** — DynamoDB (sessions + results)

All deploy commands use `Makefile.deploy` and must be run from the `fantasy_football/` directory.

### Prerequisites

- AWS CLI v2 (`aws --version` should show `aws-cli/2.x`)
- Docker
- Node.js 20+
- Vercel CLI (`npm install -g vercel`)
- AWS credentials configured (`aws sts get-caller-identity` should succeed)

### Step 1 — Yahoo Developer App

Create a Yahoo app at [developer.yahoo.com/apps](https://developer.yahoo.com/apps/):

1. Application type: **Web Application**
2. API Permissions: **Fantasy Sports (Read)**
3. Redirect URI: `https://<your-app-runner-url>/auth/callback`
   (You can use a placeholder for now and update it after App Runner is deployed.)

Note your **Client ID** and **Client Secret** — you'll need them as environment variables.

### Step 2 — One-time AWS infrastructure

Creates the DynamoDB tables, ECR repository, and two IAM roles:
- `AppRunnerECRAccessRole` — used by App Runner to pull the Docker image from ECR
- `AppRunnerInstanceRole` — assumed by the running container to read/write DynamoDB

```
make -f Makefile.deploy infra
```

This is safe to run once per resource (AWS will error on duplicates, which can be ignored).

### Step 3 — Build and push the Docker image

```
make -f Makefile.deploy docker-build
make -f Makefile.deploy docker-push
```

The build context is the `fantasy_football/` directory. The image includes `ff_luck.py` and
`yahoo_api.py` alongside the backend source.

### Step 4 — Create the App Runner service

```
make -f Makefile.deploy apprunner-create
```

After the command completes, from the JSON output:

1. Copy the `ServiceArn` — you'll need it for future redeploys and GitHub Actions.
2. Copy the `ServiceUrl` — this is your backend's public HTTPS hostname.
3. **In the App Runner console**, open the service → Configuration → Service settings →
   set **Request timeout** to **600 seconds**. This is required for SSE streams to complete.

Update the Yahoo app's redirect URI to:
```
https://<ServiceUrl>/auth/callback
```

### Step 5 — Configure App Runner environment variables

In the App Runner console, add these environment variables to the service:

| Variable | Value |
|---|---|
| `YAHOO_CONSUMER_KEY` | From your Yahoo app |
| `YAHOO_CONSUMER_SECRET` | From your Yahoo app |
| `YAHOO_REDIRECT_URI` | `https://<ServiceUrl>/auth/callback` |
| `AWS_DEFAULT_REGION` | `us-east-1` |

The `AppRunnerInstanceRole` created in Step 2 already has the required DynamoDB permissions —
no additional policy configuration needed.

### Step 6 — Deploy the frontend

Update `frontend/vercel.json` — replace `REPLACE_WITH_APP_RUNNER_URL` with your App Runner
`ServiceUrl` (no `https://` prefix, just the hostname):

```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://<ServiceUrl>/api/:path*" },
    { "source": "/auth/:path*", "destination": "https://<ServiceUrl>/auth/:path*" },
    { "source": "/((?!api|auth).*)", "destination": "/index.html" }
  ]
}
```

Then deploy:

```
make -f Makefile.deploy frontend-deploy
```

Follow the Vercel CLI prompts on first run to link the project to your Vercel account.
Vercel provides HTTPS automatically — no certificate setup needed.

---

## GitHub Actions (CI/CD)

Subsequent deploys on push to `master` are handled by `.github/workflows/`.

### Required GitHub secrets

Go to the repository → Settings → Secrets and variables → Actions, and add:

| Secret | How to get it |
|---|---|
| `AWS_DEPLOY_ROLE_ARN` | ARN of an IAM role with OIDC trust for GitHub Actions (see below) |
| `APP_RUNNER_SERVICE_ARN` | From the `apprunner-create` output in Step 4 |
| `VERCEL_TOKEN` | vercel.com → Account Settings → Tokens |
| `VERCEL_ORG_ID` | Run `vercel whoami --token <token>` or check Vercel project settings |
| `VERCEL_PROJECT_ID` | Vercel project settings → General |

### Setting up the AWS deploy role (OIDC)

GitHub Actions authenticates to AWS via OIDC — no long-lived access keys needed.

**1. Add GitHub as an OIDC provider in IAM** (one-time per AWS account):

```
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

**2. Create the deploy role:**

```
aws iam create-role \
  --role-name GitHubActionsDeployRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Federated": "arn:aws:iam::<account>:oidc-provider/token.actions.githubusercontent.com"},
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringLike": {"token.actions.githubusercontent.com:sub": "repo:<your-github-org>/<your-repo>:*"}
      }
    }]
  }'
```

**3. Attach the required permissions:**

```
aws iam attach-role-policy \
  --role-name GitHubActionsDeployRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser

aws iam attach-role-policy \
  --role-name GitHubActionsDeployRole \
  --policy-arn arn:aws:iam::aws:policy/AWSAppRunnerFullAccess
```

Set `AWS_DEPLOY_ROLE_ARN` to `arn:aws:iam::<account>:role/GitHubActionsDeployRole`.

### What triggers a deploy

| Push touches | Workflow triggered |
|---|---|
| `backend/`, `ff_luck.py`, or `yahoo_api.py` | `deploy-backend.yml` — rebuilds Docker image, pushes to ECR, triggers App Runner redeploy |
| `frontend/` | `deploy-frontend.yml` — runs `npm ci && npm run build`, deploys to Vercel |

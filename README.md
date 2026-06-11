# Cost Breakdown Engine

A small FinOps tool that gives you visibility into AWS infrastructure spend. It breaks costs down three ways: by category (compute / storage / network), by AWS service (EC2, EKS, RDS, S3 and so on) and by environment (dev / staging / production). On top of that it generates a handful of plain-English insights using simple rules, no AI involved.

The backend is FastAPI, the dashboard is React + Chart.js. Cost data comes from a mock JSON file that's shaped like what the AWS Cost Explorer API would return, so swapping in real billing data later only means changing the loader.

## Project layout

```
cost-breakdown-engine/
├── backend/
│   ├── main.py               # FastAPI app, all endpoints       (T4)
│   ├── models.py             # Pydantic data models             (T1)
│   ├── aggregator.py         # cost aggregation logic           (T2 + T3)
│   ├── insights.py           # rule-based insights              (T6)
│   ├── config.py             # tunable thresholds (env vars)
│   ├── data/mock_costs.json  # 26 mock AWS resources
│   └── tests/                # 33 unit + integration tests
├── frontend/                 # React dashboard                  (T5)
├── docker-compose.yml
└── .github/workflows/ci.yml  # lint, tests, vuln scanning
```

## Running it

The quickest way is Docker:

```bash
docker compose up --build
```

Dashboard at http://localhost:3000, API docs at http://localhost:8000/docs.

Or run it locally without Docker. Backend first:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Then the frontend in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

That serves the dashboard on http://localhost:5173. The Vite dev server proxies API calls to port 8000, so there's nothing else to configure.

## API

| Method | Path                        | What it returns                     |
|--------|-----------------------------|-------------------------------------|
| GET    | `/health`                   | health check                        |
| GET    | `/api/summary`              | total cost + top contributors       |
| GET    | `/api/costs/by-category`    | compute / storage / network split   |
| GET    | `/api/costs/by-service`     | cost per AWS service                |
| GET    | `/api/costs/by-environment` | dev / staging / production split    |
| GET    | `/api/resources`            | all resources, filterable           |
| GET    | `/api/insights`             | human-readable cost summaries       |

`/api/resources` takes optional `category`, `environment` and `service` query params, all case-insensitive.

A couple of examples:

```bash
curl http://localhost:8000/api/summary
# {"total_monthly_cost":2587.66,"total_resources":26,"currency":"USD",
#  "top_category":"compute","top_service":"EKS","top_environment":"production"}

curl http://localhost:8000/api/costs/by-category
# [{"category":"compute","total_cost":1365.12,"percentage":52.75,"resource_count":9}, ...]
```

The insights endpoint returns sentences like "Compute accounts for 52.8% of total spend" and "Non-production environments cost $607.80/month, which is 30.7% of production spend".

## Tests and checks

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v        # 33 tests, runs in well under a second
```

The tests check that totals reconcile against the raw data (no double counting), percentages sum to ~100, breakdowns are sorted, filters work, and every endpoint returns the right shape.

The same linters and scanners that CI runs can be run locally:

```bash
# backend
ruff check . && ruff format --check .
pip-audit

# frontend
npm run lint
npm audit --audit-level=high
```

## CI

GitHub Actions runs on every push and PR (`.github/workflows/ci.yml`):

- ruff lint + format check on the backend (includes the bandit security rules)
- pytest
- pip-audit for known CVEs in Python dependencies
- ESLint and npm audit on the frontend, then a production build
- hadolint on both Dockerfiles
- Trivy scans of the built images (fails on fixable CRITICAL/HIGH) plus a filesystem scan for misconfigurations and leaked secrets

Both container images run as non-root users, the frontend image builds with `npm ci` against the committed lockfile so builds are reproducible, and both have healthchecks that docker-compose uses for startup ordering.

## How it works

**Data model.** Each resource is a flat record: id, name, service, category, environment, region, monthly cost, tags. Flat on purpose, since that's roughly what Cost Explorer gives you.

**Aggregation.** `aggregator.py` loads the JSON and groups it with plain `defaultdict` passes. Percentages are `part / total * 100`, rounded to 2 decimals, with a shared helper that handles the zero-total case. There's no database; the file is re-read per request, which is fine at this size and keeps things stateless.

**Insights.** All rule-based. One insight per category and environment, the top 3 services, plus two "actionable" ones: a right-sizing flag when dev+staging spend goes above 30% of production spend, and a concentration flag when a single service is more than 25% of the total. The thresholds live in `config.py` and can be overridden with env vars, e.g.:

```bash
INSIGHTS_TOP_N_SERVICES=10 INSIGHTS_NON_PROD_VS_PROD_RATIO_PCT=20 uvicorn main:app
```

**Swapping in real data.** Replace `_load_resources()` in `aggregator.py` with a boto3 call to `ce.get_cost_and_usage()`. There's a sketch in the module docstring. Nothing else needs to change.

## Mock data

`backend/data/mock_costs.json` has 26 resources across 8 services and 3 environments, with costs based on rough us-east-1 on-demand pricing. Total comes to $2,587.66/month. Edit the file and refresh the dashboard to experiment; no rebuild needed.

## Assumptions and tradeoffs

- Costs are monthly, in USD, and a single snapshot. No history or month-over-month yet, though the model could take a timestamp field without much trouble.
- One AWS account, with environments told apart by tags. Real setups usually go one account per environment under AWS Organizations (better isolation, cleaner attribution, SCPs). Supporting that here would mean adding `account_id` to the model, a `/api/costs/by-account` endpoint, and grouping by `LINKED_ACCOUNT` in the Cost Explorer call. It's left out because the brief scoped this to a simple single-cloud demo.
- Categories are fixed to compute/storage/network and environments to dev/staging/production. The backend discovers values dynamically but the frontend filter tabs are hard-coded, so a new category shows up in the API immediately and needs a one-line UI change.
- Percentages are rounded, so a breakdown can sum to 99.99 or 100.01. Raw cost totals are exact.
- No pagination on `/api/resources`. Fine for 26 rows, not for a real account.
- No auth, and CORS is wide open. It's an internal read-only demo; in production this would sit behind whatever auth layer the team already has, and CORS would be locked to the frontend origin.
- Negative costs aren't rejected by the model. Treated as an input invariant for now.

## Out of scope (per the assignment brief)

Real billing integrations, AI/ML cost recommendations, multi-cloud, forecasting.

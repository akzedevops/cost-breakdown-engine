# Cost Breakdown Engine

A FinOps layer that gives engineers clear visibility into AWS infrastructure spend — broken down by **category**, **AWS service**, and **environment**, with rule-based insights surfaced on top.

> Take-home assignment for the Backend DevOps Engineer role at White Code Labs.

---

## At a Glance

| | |
|---|---|
| **What it does** | Ingests cost data, groups it three ways, generates plain-English insights |
| **Stack** | FastAPI · Pydantic v2 · React 18 · Vite · Chart.js |
| **Tests** | 33 pytest cases · all passing in under 0.5s |
| **Run with** | One command via Docker Compose, or local Python + Node |
| **Dataset** | 26 mock AWS resources across 8 services and 3 environments |
| **Sample total** | `$2,587.66/month` · Compute 52.75% · Production 76.51% |

---

## Overview

The system ingests structured infrastructure cost data and produces:

- Cost breakdown by **category** — compute / storage / network
- Cost breakdown by **AWS service** — EC2, EKS, RDS, S3, EBS, ELB, CloudFront, DataTransfer
- Cost breakdown by **environment** — dev / staging / production
- Rule-based **human-readable insights** (no AI/ML)

Mock data simulates what the AWS Cost Explorer API (`ce.get_cost_and_usage`) would return in production. The data source is intentionally decoupled from the aggregation engine — see [backend/aggregator.py](backend/aggregator.py) for the swap-in point.

---

## Project Structure

```
cost-breakdown-engine/
├── backend/
│   ├── main.py               # FastAPI app — all API endpoints           (T4)
│   ├── models.py             # Pydantic data models                       (T1)
│   ├── aggregator.py         # Cost aggregation engine                    (T2 + T3)
│   ├── insights.py           # Rule-based insights generator              (T6)
│   ├── config.py             # Pydantic Settings — env-overridable thresholds
│   ├── data/
│   │   └── mock_costs.json   # 26 mock AWS resources
│   ├── tests/                # 33 unit + integration tests
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── Dockerfile
├── frontend/                 # React dashboard                            (T5)
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   │       ├── SummaryCards.jsx
│   │       ├── CategoryChart.jsx     # Doughnut chart
│   │       ├── EnvironmentChart.jsx  # Bar chart
│   │       ├── ServiceTable.jsx      # Filterable table
│   │       └── InsightsPanel.jsx
│   ├── vite.config.js
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

Each module is tagged with the ticket it implements (T1–T6). The mapping also appears as comments at the top of every file.

---

## Quick Start

### Option A — Docker Compose (one command)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
docker compose up --build
```

- **Dashboard** → http://localhost:3000
- **API docs** → http://localhost:8000/docs

Stop with `Ctrl+C` then `docker compose down`.

### Option B — Run locally without Docker

**Backend**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
# API at http://localhost:8000 · Swagger UI at http://localhost:8000/docs
```

**Frontend** (in a separate terminal)
```bash
cd frontend
npm install
npm run dev
# Dashboard at http://localhost:5173
```

The Vite dev server proxies `/api` and `/health` to `localhost:8000`, so no CORS or env-var setup is required.

---

## API Endpoints

| Method | Path                          | Description                          |
|--------|-------------------------------|--------------------------------------|
| GET    | `/health`                     | Health check                         |
| GET    | `/api/summary`                | Total cost + top contributors        |
| GET    | `/api/costs/by-category`      | Compute / storage / network split    |
| GET    | `/api/costs/by-service`       | Cost per AWS service                 |
| GET    | `/api/costs/by-environment`   | Dev / staging / production split     |
| GET    | `/api/resources`              | All resources, filterable            |
| GET    | `/api/insights`               | Rule-based human-readable summaries  |

Interactive OpenAPI docs are available at **http://localhost:8000/docs**.

### Example responses

**GET /api/summary**
```json
{
  "total_monthly_cost": 2587.66,
  "total_resources": 26,
  "currency": "USD",
  "top_category": "compute",
  "top_service": "EKS",
  "top_environment": "production"
}
```

**GET /api/costs/by-category**
```json
[
  { "category": "compute", "total_cost": 1365.12, "percentage": 52.75, "resource_count": 9 },
  { "category": "storage", "total_cost": 946.20,  "percentage": 36.57, "resource_count": 11 },
  { "category": "network", "total_cost": 276.34,  "percentage": 10.68, "resource_count": 6 }
]
```

**GET /api/insights** (excerpt)
```json
{
  "summary": "Total monthly AWS spend is $2,587.66. Compute is the largest cost category, EKS is the top individual service, and production is the highest-spend environment.",
  "insights": [
    { "type": "category", "message": "Compute accounts for 52.8% of total spend ($1,365.12/month across 9 resources)." },
    { "type": "service",  "message": "EKS is costing $720.00/month (27.8% of total spend)." },
    { "type": "general",  "message": "Non-production environments cost $607.80/month, which is 30.7% of production spend — consider right-sizing dev/staging resources to reduce waste." }
  ]
}
```

---

## Testing Cost Breakdown Outputs

```bash
# Unit + integration tests (FastAPI TestClient, no live server needed)
cd backend
pip install -r requirements-dev.txt
pytest -v
# → 33 passed
```

Smoke-test against a running server:

```bash
curl http://localhost:8000/api/summary
curl http://localhost:8000/api/costs/by-category
curl "http://localhost:8000/api/resources?environment=production"
curl "http://localhost:8000/api/resources?category=compute"
curl http://localhost:8000/api/insights
```

The test suite covers:

- Total cost matches the sum of raw resource costs (no double counting)
- Category / service / environment percentages each sum to ~100
- Resource counts match the underlying data file
- Sorted-by-cost contract on every breakdown
- Edge cases: zero-total handling, case-insensitive filters
- End-to-end shape of every API response

---

## Mock Data

[`backend/data/mock_costs.json`](backend/data/mock_costs.json) contains 26 AWS resources spanning:

| Category | Services                       | Environments             |
|----------|--------------------------------|--------------------------|
| Compute  | EC2, EKS                       | dev, staging, production |
| Storage  | S3, EBS, RDS                   | dev, staging, production |
| Network  | ELB, CloudFront, DataTransfer  | dev, staging, production |

Costs are based on representative AWS on-demand pricing in `us-east-1`.

To experiment, edit the JSON and refresh the dashboard — no rebuild required.

---

## Implementation Notes

### Data modelling (T1)

Each resource is a flat record carrying `category`, `service`, `environment`, `region`, `monthly_cost`, and free-form `tags`. The flat shape is intentional — it mirrors what AWS Cost Explorer returns, so the swap from mock to live data only changes the loader.

### Aggregation logic (T2 + T3)

[`backend/aggregator.py`](backend/aggregator.py) uses Python `defaultdict` to group costs in a single pass per dimension. Percentages are computed as `(part / total) * 100` with a single shared helper that handles the zero-total edge case. There is no database — the data is loaded from JSON on each request, which is plenty fast at this scale and keeps the demo stateless.

### Insights logic (T6)

[`backend/insights.py`](backend/insights.py) applies deterministic rules:

- One insight per category, ordered by spend
- Top three services flagged with their share of total spend
- One insight per environment
- General insight if **non-production spend exceeds 30%** of production spend — a common FinOps right-sizing signal
- General insight if **the top service exceeds 25%** of total spend — flags concentration risk

No ML, no external calls, fully deterministic.

### Frontend (T5)

A single-page React app talks to the API over a Vite proxy in dev and through nginx in production. The dashboard surfaces:

- Four summary cards (total spend, top category, top service, top environment)
- Doughnut chart for category split
- Bar chart for environment split
- Filterable service-level table with a percentage bar per row
- Insights panel with the overall summary plus rule-based callouts

### Production swap-in

Replace `_load_resources()` in [`backend/aggregator.py`](backend/aggregator.py) with a `boto3` call to `ce.get_cost_and_usage()` — a sketch is in the module docstring. The aggregation layer, API, and UI require zero further changes.

---

## Assumptions

Listed proactively so a reviewer doesn't have to dig for them.

### Scope & data

- **Costs are monthly and in USD.** No currency conversion, no daily/hourly granularity.
- **Snapshot-only — no time dimension.** Costs are a single monthly figure per resource. No month-over-month history. The `Resource` model can absorb a `timestamp` field cleanly when needed.
- **Monthly costs are non-negative.** No validation rejects negative values today — it's an invariant of the input, not an enforced constraint.

### Account model — deliberate simplification

The mock dataset models **a single AWS account with environments distinguished by tags** (`environment: dev | staging | production` on each resource). This is one valid real-world pattern, but it isn't the AWS-recommended best practice.

**Production-correct pattern** is **one AWS account per environment** under AWS Organizations:

```
AWS Organizations
├── prod-account        ← production workloads only
├── staging-account
├── dev-account
└── shared-services-account
```

Reasons real estates do it this way: blast-radius isolation, clean cost attribution without tag discipline, Service Control Policies to gate expensive services in dev, compliance boundaries, separate service quotas.

**What would change to support multi-account** (out of scope per the brief, but mapped out for completeness):

- `Resource` model gains `account_id: str` and `account_alias: str`
- New endpoint: `GET /api/costs/by-account`
- The boto3 swap-in groups by Cost Explorer's `LINKED_ACCOUNT` dimension instead of an `Environment` tag:
  ```python
  GroupBy=[{"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"}]
  ```
- Aggregation engine itself is unchanged — it would gain one more grouping function alongside the existing three.

Single-account-with-env-tags was chosen here because the brief explicitly scopes to a single cloud and the multi-account model adds AWS Organizations concepts (consolidated billing, SCPs, account hierarchy) that aren't in scope for a cost-breakdown demo.

### Taxonomy

- **Categories are exactly `{compute, storage, network}`** and **environments are exactly `{dev, staging, production}`.** The backend aggregation discovers values dynamically, but the frontend filter tabs and env display order are hard-coded to these three. Adding a fourth category works in the API immediately; surfacing it in the UI is a one-line change.
- **Environment display order is fixed: `production → staging → dev`** (by importance, not by cost). Coded in `aggregator.get_by_environment()`.
- **Service names are stored case-sensitively** (`"EKS"`, `"S3"`) but the `/api/resources?service=…` filter is case-insensitive for ergonomics.
- **Tags are free-form `dict[str, str]`** with no schema enforcement — matches AWS's tag model.

### Aggregation & display

- **Percentages are rounded to 2 decimal places.** A dimension with many buckets can therefore sum to 99.99% or 100.01% from rounding drift — standard FinOps tool behaviour. AWS Cost Explorer does the same.
- **Raw cost totals are exact** and reconcile against the sum of individual resource costs.
- **Sort order is descending by cost** for categories and services; environments use the fixed importance order above.
- **No pagination on `/api/resources`.** Fine at 26 resources; would need cursor-based pagination at AWS-account scale.

### Insights (rule-based, no AI)

All thresholds live in [`backend/config.py`](backend/config.py) as a typed Pydantic Settings class and are overridable at runtime via `INSIGHTS_*` environment variables. Defaults:

- **30%** — flag if non-production spend exceeds 30% of production spend (right-sizing signal). Override: `INSIGHTS_NON_PROD_VS_PROD_RATIO_PCT`
- **25%** — flag if the top single service exceeds 25% of total spend (concentration risk). Override: `INSIGHTS_TOP_SERVICE_CONCENTRATION_PCT`
- **Top 3 services** surfaced as individual callouts. Override: `INSIGHTS_TOP_N_SERVICES`

Example: tune for a larger estate without touching code:
```bash
INSIGHTS_TOP_N_SERVICES=10 INSIGHTS_NON_PROD_VS_PROD_RATIO_PCT=20 uvicorn main:app
```

### Operations

- **No authentication on the API.** Suitable for an internal tooling demo; in production this would sit behind the team's existing auth layer (Cognito, IAM, OIDC, whatever the org uses).
- **CORS is currently permissive (`*`).** Comment in `main.py` notes this should be locked to the deployed frontend origin in production.
- **Backend is stateless.** Mock JSON is loaded fresh on every request — no DB, no cache. Plenty fast at this scale, trivial to swap for `boto3.ce.get_cost_and_usage()`.

### Dependencies & packaging

- **Runtime vs dev dependencies are split into two files** — standard Python convention.
  - `backend/requirements.txt` — just the three runtime packages (`fastapi`, `uvicorn`, `pydantic`). This is what the production Docker image installs.
  - `backend/requirements-dev.txt` — pulls in `requirements.txt` via `-r` then adds `pytest` and `httpx` for the test suite.
- **Why the split:** keeps the production container lean (test tooling has no business in a prod image), makes the runtime dependency footprint explicit, and gives CI a clean caching boundary between runtime and dev installs.
- **Install paths:** production / Docker uses `pip install -r requirements.txt`; local development uses `pip install -r requirements-dev.txt` to also get the test tooling.

### Explicitly out of scope (per the assignment brief)

- Real-time billing integrations
- AI/ML-based cost optimisation recommendations
- Multi-cloud support
- Forecasting / predictive analytics

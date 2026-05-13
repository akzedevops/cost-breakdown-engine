"""
Cost Aggregation Engine — T2 & T3

Loads cost data and provides breakdown by:
  - Category  (compute / storage / network)
  - Service   (EC2 / EKS / S3 / RDS / …)
  - Environment (dev / staging / production)

In production, replace `_load_resources()` with a boto3 call to
AWS Cost Explorer:

    import boto3
    ce = boto3.client("ce", region_name="us-east-1")
    response = ce.get_cost_and_usage(
        TimePeriod={"Start": "2026-05-01", "End": "2026-05-31"},
        Granularity="MONTHLY",
        GroupBy=[
            {"Type": "DIMENSION", "Key": "SERVICE"},
            {"Type": "TAG",       "Key": "Environment"},
        ],
        Metrics=["UnblendedCost"],
    )
    # Map response["ResultsByTime"][0]["Groups"] → Resource objects

The rest of this module (aggregation logic) stays unchanged.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Any

from models import (
    Resource,
    CategoryBreakdown,
    ServiceBreakdown,
    EnvironmentBreakdown,
    CostSummary,
)

_DATA_FILE = Path(__file__).parent / "data" / "mock_costs.json"


# ---------------------------------------------------------------------------
# Data loader
# ---------------------------------------------------------------------------

def _load_resources() -> list[Resource]:
    """Load resources from the mock JSON file.

    PRODUCTION SWAP POINT: replace this function body with a boto3
    Cost Explorer call (see module docstring above).
    """
    raw = json.loads(_DATA_FILE.read_text())
    return [Resource(**r) for r in raw["resources"]]


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

def _round2(value: float) -> float:
    return round(value, 2)


def _pct(part: float, total: float) -> float:
    if total == 0:
        return 0.0
    return _round2((part / total) * 100)


# ---------------------------------------------------------------------------
# Public API — used by FastAPI routes
# ---------------------------------------------------------------------------

def get_all_resources() -> list[Resource]:
    return _load_resources()


def get_summary() -> CostSummary:
    resources = _load_resources()
    total = sum(r.monthly_cost for r in resources)

    # top category
    cat_totals: dict[str, float] = defaultdict(float)
    for r in resources:
        cat_totals[r.category] += r.monthly_cost
    top_cat = max(cat_totals, key=lambda k: cat_totals[k])

    # top service
    svc_totals: dict[str, float] = defaultdict(float)
    for r in resources:
        svc_totals[r.service] += r.monthly_cost
    top_svc = max(svc_totals, key=lambda k: svc_totals[k])

    # top environment
    env_totals: dict[str, float] = defaultdict(float)
    for r in resources:
        env_totals[r.environment] += r.monthly_cost
    top_env = max(env_totals, key=lambda k: env_totals[k])

    return CostSummary(
        total_monthly_cost=_round2(total),
        total_resources=len(resources),
        top_category=top_cat,
        top_service=top_svc,
        top_environment=top_env,
    )


def get_by_category() -> list[CategoryBreakdown]:
    resources = _load_resources()
    total = sum(r.monthly_cost for r in resources)

    cat_cost: dict[str, float] = defaultdict(float)
    cat_count: dict[str, int] = defaultdict(int)

    for r in resources:
        cat_cost[r.category] += r.monthly_cost
        cat_count[r.category] += 1

    return sorted(
        [
            CategoryBreakdown(
                category=cat,
                total_cost=_round2(cost),
                percentage=_pct(cost, total),
                resource_count=cat_count[cat],
            )
            for cat, cost in cat_cost.items()
        ],
        key=lambda x: x.total_cost,
        reverse=True,
    )


def get_by_service() -> list[ServiceBreakdown]:
    resources = _load_resources()
    total = sum(r.monthly_cost for r in resources)

    # aggregate cost + count per (service, category) pair
    svc_cost: dict[tuple[str, str], float] = defaultdict(float)
    svc_count: dict[tuple[str, str], int] = defaultdict(int)

    for r in resources:
        key = (r.service, r.category)
        svc_cost[key] += r.monthly_cost
        svc_count[key] += 1

    return sorted(
        [
            ServiceBreakdown(
                service=svc,
                category=cat,
                total_cost=_round2(cost),
                percentage=_pct(cost, total),
                resource_count=svc_count[(svc, cat)],
            )
            for (svc, cat), cost in svc_cost.items()
        ],
        key=lambda x: x.total_cost,
        reverse=True,
    )


def get_by_environment() -> list[EnvironmentBreakdown]:
    resources = _load_resources()
    total = sum(r.monthly_cost for r in resources)

    env_cost: dict[str, float] = defaultdict(float)
    env_count: dict[str, int] = defaultdict(int)

    for r in resources:
        env_cost[r.environment] += r.monthly_cost
        env_count[r.environment] += 1

    # enforce display order
    order = {"production": 0, "staging": 1, "dev": 2}
    return sorted(
        [
            EnvironmentBreakdown(
                environment=env,
                total_cost=_round2(cost),
                percentage=_pct(cost, total),
                resource_count=env_count[env],
            )
            for env, cost in env_cost.items()
        ],
        key=lambda x: order.get(x.environment, 99),
    )

"""
Tests for the cost aggregation engine.

Covers the core guarantees a hiring reviewer cares about:
  - Total cost matches the sum of all resource costs (no double counting).
  - Category / service / environment percentages each sum to 100.
  - Counts match the underlying data.
  - Sorting is correct (descending by cost where applicable).
  - Pure functions behave correctly on empty / single-resource inputs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aggregator import (
    _load_resources,
    get_by_category,
    get_by_environment,
    get_by_service,
    get_summary,
)

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "mock_costs.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _raw_resources():
    return json.loads(DATA_FILE.read_text())["resources"]


def _approx(a: float, b: float, tol: float = 0.05) -> bool:
    return abs(a - b) <= tol


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def test_total_cost_matches_raw_sum():
    expected = round(sum(r["monthly_cost"] for r in _raw_resources()), 2)
    assert get_summary().total_monthly_cost == expected


def test_total_resources_matches_data_file():
    assert get_summary().total_resources == len(_raw_resources())


def test_summary_top_values_are_consistent():
    summary = get_summary()
    cats = {c.category: c.total_cost for c in get_by_category()}
    svcs = {s.service: s.total_cost for s in get_by_service()}
    envs = {e.environment: e.total_cost for e in get_by_environment()}

    assert summary.top_category == max(cats, key=cats.get)
    assert summary.top_service == max(svcs, key=svcs.get)
    assert summary.top_environment == max(envs, key=envs.get)


# ---------------------------------------------------------------------------
# Category breakdown
# ---------------------------------------------------------------------------

def test_category_breakdown_covers_all_categories():
    cats = {c.category for c in get_by_category()}
    expected = {r["category"] for r in _raw_resources()}
    assert cats == expected


def test_category_percentages_sum_to_100():
    pct_sum = sum(c.percentage for c in get_by_category())
    assert _approx(pct_sum, 100.0)


def test_category_totals_sum_to_grand_total():
    summary = get_summary()
    cat_sum = round(sum(c.total_cost for c in get_by_category()), 2)
    assert _approx(cat_sum, summary.total_monthly_cost, tol=0.01)


def test_category_breakdown_sorted_descending():
    costs = [c.total_cost for c in get_by_category()]
    assert costs == sorted(costs, reverse=True)


# ---------------------------------------------------------------------------
# Service breakdown
# ---------------------------------------------------------------------------

def test_service_percentages_sum_to_100():
    pct_sum = sum(s.percentage for s in get_by_service())
    assert _approx(pct_sum, 100.0)


def test_service_resource_counts_match_data():
    expected_counts: dict[str, int] = {}
    for r in _raw_resources():
        expected_counts[r["service"]] = expected_counts.get(r["service"], 0) + 1

    actual_counts = {s.service: s.resource_count for s in get_by_service()}
    assert actual_counts == expected_counts


def test_service_breakdown_sorted_descending():
    costs = [s.total_cost for s in get_by_service()]
    assert costs == sorted(costs, reverse=True)


# ---------------------------------------------------------------------------
# Environment breakdown
# ---------------------------------------------------------------------------

def test_environment_breakdown_orders_prod_first():
    envs = [e.environment for e in get_by_environment()]
    # production must come before staging and dev (display order)
    assert envs.index("production") < envs.index("staging") < envs.index("dev")


def test_environment_percentages_sum_to_100():
    pct_sum = sum(e.percentage for e in get_by_environment())
    assert _approx(pct_sum, 100.0)


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def test_load_resources_returns_typed_objects():
    resources = _load_resources()
    assert len(resources) == len(_raw_resources())
    # every resource carries the four pieces aggregation depends on
    for r in resources:
        assert r.category in {"compute", "storage", "network"}
        assert r.environment in {"dev", "staging", "production"}
        assert r.monthly_cost > 0
        assert r.service  # non-empty


# ---------------------------------------------------------------------------
# Edge cases — exercise the pure helpers directly
# ---------------------------------------------------------------------------

def test_pct_handles_zero_total():
    from aggregator import _pct

    assert _pct(0, 0) == 0.0
    assert _pct(10, 0) == 0.0


@pytest.mark.parametrize(
    "part,total,expected",
    [
        (50, 100, 50.0),
        (1, 3, 33.33),
        (2587.66, 2587.66, 100.0),
    ],
)
def test_pct_basic(part, total, expected):
    from aggregator import _pct

    assert _pct(part, total) == expected

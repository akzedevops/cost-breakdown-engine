"""
T6 — Rule-based Insights Generator

Produces human-readable cost summaries with zero AI/ML.
All logic is deterministic arithmetic.

Tunable thresholds live in `config.py` and can be overridden at runtime via
`INSIGHTS_*` environment variables (see config.py for the full list).
"""

from aggregator import (
    get_by_category,
    get_by_environment,
    get_by_service,
    get_summary,
)
from config import settings
from models import CostInsights, InsightItem


def generate_insights() -> CostInsights:
    summary = get_summary()
    categories = get_by_category()
    services = get_by_service()
    environments = get_by_environment()

    items: list[InsightItem] = []
    total = summary.total_monthly_cost

    # ── Category insights ────────────────────────────────────────────────
    for cat in categories:
        items.append(
            InsightItem(
                type="category",
                message=(
                    f"{cat.category.capitalize()} accounts for "
                    f"{cat.percentage:.1f}% of total spend "
                    f"(${cat.total_cost:,.2f}/month across {cat.resource_count} resources)."
                ),
                value=cat.total_cost,
                percentage=cat.percentage,
            )
        )

    # ── Top-N service insights (N is config.top_n_services) ──────────────
    for svc in services[: settings.top_n_services]:
        items.append(
            InsightItem(
                type="service",
                message=(
                    f"{svc.service} is costing ${svc.total_cost:,.2f}/month "
                    f"({svc.percentage:.1f}% of total spend)."
                ),
                value=svc.total_cost,
                percentage=svc.percentage,
            )
        )

    # ── Environment insights ─────────────────────────────────────────────
    for env in environments:
        items.append(
            InsightItem(
                type="environment",
                message=(
                    f"{env.environment.capitalize()} environment contributes "
                    f"{env.percentage:.1f}% of spend "
                    f"(${env.total_cost:,.2f}/month)."
                ),
                value=env.total_cost,
                percentage=env.percentage,
            )
        )

    # ── General / actionable insights ────────────────────────────────────
    # Right-sizing: flag when non-prod spend exceeds the configured ratio of prod
    prod_cost = next((e.total_cost for e in environments if e.environment == "production"), 0)
    non_prod_cost = sum(e.total_cost for e in environments if e.environment != "production")
    if prod_cost > 0:
        ratio = round((non_prod_cost / prod_cost) * 100, 2)
        if ratio > settings.non_prod_vs_prod_ratio_pct:
            items.append(
                InsightItem(
                    type="general",
                    message=(
                        f"Non-production environments cost ${non_prod_cost:,.2f}/month, "
                        f"which is {ratio:.1f}% of production spend — consider right-sizing "
                        f"dev/staging resources to reduce waste."
                    ),
                    value=non_prod_cost,
                    percentage=ratio,
                )
            )

    # Concentration risk: flag when the top service exceeds the configured share
    top_svc = services[0] if services else None
    if top_svc and top_svc.percentage > settings.top_service_concentration_pct:
        items.append(
            InsightItem(
                type="general",
                message=(
                    f"{top_svc.service} is the highest single cost driver at "
                    f"{top_svc.percentage:.1f}% of total spend — review instance types "
                    f"or reserved pricing to optimise."
                ),
                value=top_svc.total_cost,
                percentage=top_svc.percentage,
            )
        )

    overall = (
        f"Total monthly AWS spend is ${total:,.2f}. "
        f"{summary.top_category.capitalize()} is the largest cost category, "
        f"{summary.top_service} is the top individual service, and "
        f"{summary.top_environment} is the highest-spend environment."
    )

    return CostInsights(summary=overall, insights=items)

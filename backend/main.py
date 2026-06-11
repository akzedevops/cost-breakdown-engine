"""
Cost Breakdown Engine — FastAPI Application (T4)

Endpoints:
  GET /api/summary             → total cost + top contributors
  GET /api/costs/by-category   → compute / storage / network breakdown
  GET /api/costs/by-service    → cost per AWS service
  GET /api/costs/by-environment→ dev / staging / production breakdown
  GET /api/resources           → raw resource list (filterable)
  GET /api/insights            → rule-based human-readable summaries
  GET /health                  → health check
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from aggregator import (
    get_all_resources,
    get_by_category,
    get_by_environment,
    get_by_service,
    get_summary,
)
from insights import generate_insights
from models import (
    CategoryBreakdown,
    CostInsights,
    CostSummary,
    EnvironmentBreakdown,
    Resource,
    ServiceBreakdown,
)

app = FastAPI(
    title="Cost Breakdown Engine",
    description=(
        "FinOps layer — AWS infrastructure cost visibility by category, service, and environment."
    ),
    version="1.0.0",
)

# Permissive CORS — this is an internal read-only demo with no credentials.
# In production, lock this down to the deployed frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "cost-breakdown-engine"}


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


@app.get("/api/summary", response_model=CostSummary, tags=["Costs"])
def summary():
    """Total monthly cost + top category, service, and environment."""
    return get_summary()


# ---------------------------------------------------------------------------
# Breakdowns
# ---------------------------------------------------------------------------


@app.get("/api/costs/by-category", response_model=list[CategoryBreakdown], tags=["Costs"])
def costs_by_category():
    """Cost split across compute, storage, and network — sorted by spend."""
    return get_by_category()


@app.get("/api/costs/by-service", response_model=list[ServiceBreakdown], tags=["Costs"])
def costs_by_service():
    """Cost per AWS service (EC2, EKS, RDS, S3, …) — sorted by spend."""
    return get_by_service()


@app.get("/api/costs/by-environment", response_model=list[EnvironmentBreakdown], tags=["Costs"])
def costs_by_environment():
    """Cost split across dev, staging, and production."""
    return get_by_environment()


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@app.get("/api/resources", response_model=list[Resource], tags=["Resources"])
def resources(
    category: str | None = Query(
        None, description="Filter by category: compute | storage | network"
    ),
    environment: str | None = Query(
        None, description="Filter by environment: dev | staging | production"
    ),
    service: str | None = Query(None, description="Filter by service, e.g. EC2"),
):
    """List all resources with optional filters."""
    items = get_all_resources()
    if category:
        items = [r for r in items if r.category == category.lower()]
    if environment:
        items = [r for r in items if r.environment == environment.lower()]
    if service:
        items = [r for r in items if r.service.lower() == service.lower()]
    return sorted(items, key=lambda r: r.monthly_cost, reverse=True)


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------


@app.get("/api/insights", response_model=CostInsights, tags=["Insights"])
def insights():
    """Rule-based human-readable cost summaries and recommendations."""
    return generate_insights()

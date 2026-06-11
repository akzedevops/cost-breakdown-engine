"""
Data models for the Cost Breakdown Engine.
Pydantic v2 models for request/response validation and serialisation.
"""

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Core resource model (matches mock_costs.json schema)
# ---------------------------------------------------------------------------


class Resource(BaseModel):
    resource_id: str
    name: str
    service: str  # EC2 | EKS | S3 | EBS | RDS | ELB | CloudFront | DataTransfer
    category: str  # compute | storage | network
    environment: str  # dev | staging | production
    monthly_cost: float
    region: str
    unit: str = "USD"
    tags: dict = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Response models — returned by API endpoints
# ---------------------------------------------------------------------------


class CategoryBreakdown(BaseModel):
    category: str
    total_cost: float
    percentage: float
    resource_count: int


class ServiceBreakdown(BaseModel):
    service: str
    category: str
    total_cost: float
    percentage: float
    resource_count: int


class EnvironmentBreakdown(BaseModel):
    environment: str
    total_cost: float
    percentage: float
    resource_count: int


class CostSummary(BaseModel):
    total_monthly_cost: float
    total_resources: int
    currency: str = "USD"
    top_category: str
    top_service: str
    top_environment: str


class InsightItem(BaseModel):
    type: str  # "category" | "service" | "environment" | "general"
    message: str
    value: float | None = None
    percentage: float | None = None


class CostInsights(BaseModel):
    summary: str
    insights: list[InsightItem]

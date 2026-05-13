"""
Runtime configuration for the Cost Breakdown Engine.

Uses Pydantic Settings so every tunable lives in one typed, documented class
and can be overridden at runtime via environment variables — the standard
12-factor config pattern recommended by the FastAPI docs.

Override examples
-----------------
    INSIGHTS_NON_PROD_VS_PROD_RATIO_PCT=40 uvicorn main:app
    INSIGHTS_TOP_N_SERVICES=5 pytest

Tests can override values cleanly via monkeypatch.setattr(settings, ...).
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class InsightSettings(BaseSettings):
    """Thresholds that drive the rule-based insights engine."""

    model_config = SettingsConfigDict(
        env_prefix="INSIGHTS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    non_prod_vs_prod_ratio_pct: float = Field(
        default=30.0,
        ge=0,
        le=1000,
        description=(
            "Flag a right-sizing insight when combined dev+staging spend "
            "exceeds this percentage of production spend."
        ),
    )

    top_service_concentration_pct: float = Field(
        default=25.0,
        ge=0,
        le=100,
        description=(
            "Flag a concentration-risk insight when the highest-spend "
            "service exceeds this percentage of total spend."
        ),
    )

    top_n_services: int = Field(
        default=3,
        ge=1,
        le=20,
        description="How many top services to surface as individual insights.",
    )


# Single shared instance — import this everywhere.
settings = InsightSettings()

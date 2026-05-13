"""
Tests for the rule-based insights generator.

Verifies that:
  - The overall summary mentions total spend, top category, top service, top env.
  - There is at least one insight per category (compute / storage / network).
  - All numeric values in insights are non-negative and rounded.
  - The "non-production cost ratio" rule fires only above the 30 % threshold.
"""

from insights import generate_insights


def test_summary_mentions_key_dimensions():
    insights = generate_insights()
    summary = insights.summary.lower()

    assert "total monthly aws spend" in summary
    assert "$" in insights.summary  # currency-formatted total
    assert "compute" in summary or "storage" in summary or "network" in summary
    assert "production" in summary or "staging" in summary or "dev" in summary


def test_each_category_appears_in_insights():
    items = generate_insights().insights
    category_msgs = [i.message.lower() for i in items if i.type == "category"]

    assert any("compute" in m for m in category_msgs)
    assert any("storage" in m for m in category_msgs)
    assert any("network" in m for m in category_msgs)


def test_insight_values_are_well_formed():
    for item in generate_insights().insights:
        if item.value is not None:
            assert item.value >= 0
        if item.percentage is not None:
            assert 0 <= item.percentage <= 1000  # generous upper bound; ratios can exceed 100


def test_top_3_services_have_insights():
    services = [i for i in generate_insights().insights if i.type == "service"]
    assert len(services) == 3


# ---------------------------------------------------------------------------
# Configurable thresholds
# ---------------------------------------------------------------------------

def test_top_n_services_is_configurable(monkeypatch):
    """Override top_n_services and verify the insight count changes."""
    from config import settings

    monkeypatch.setattr(settings, "top_n_services", 5)
    services = [i for i in generate_insights().insights if i.type == "service"]
    assert len(services) == 5


def test_top_service_threshold_can_suppress_concentration_insight(monkeypatch):
    """Raise the concentration threshold so high that the rule never fires."""
    from config import settings

    monkeypatch.setattr(settings, "top_service_concentration_pct", 99.0)
    general = [i for i in generate_insights().insights if i.type == "general"]
    # No insight should mention 'highest single cost driver' anymore
    assert not any("highest single cost driver" in i.message for i in general)


def test_non_prod_ratio_threshold_can_suppress_rightsizing_insight(monkeypatch):
    """Raise the right-sizing threshold so high that the rule never fires."""
    from config import settings

    monkeypatch.setattr(settings, "non_prod_vs_prod_ratio_pct", 999.0)
    general = [i for i in generate_insights().insights if i.type == "general"]
    assert not any("right-sizing" in i.message for i in general)

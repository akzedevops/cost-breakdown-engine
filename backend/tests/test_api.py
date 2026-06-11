"""
Integration tests for the FastAPI surface.

Uses FastAPI's TestClient so every endpoint is exercised end-to-end without
needing a running uvicorn process.
"""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_summary_endpoint_shape():
    r = client.get("/api/summary")
    assert r.status_code == 200
    body = r.json()
    assert {
        "total_monthly_cost",
        "total_resources",
        "currency",
        "top_category",
        "top_service",
        "top_environment",
    } <= body.keys()


def test_by_category_endpoint():
    r = client.get("/api/costs/by-category")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 3
    assert {c["category"] for c in body} == {"compute", "storage", "network"}


def test_by_service_endpoint_sorted_desc():
    r = client.get("/api/costs/by-service")
    assert r.status_code == 200
    costs = [s["total_cost"] for s in r.json()]
    assert costs == sorted(costs, reverse=True)


def test_by_environment_endpoint():
    r = client.get("/api/costs/by-environment")
    assert r.status_code == 200
    envs = [e["environment"] for e in r.json()]
    assert envs == ["production", "staging", "dev"]


def test_resources_filter_by_category():
    r = client.get("/api/resources", params={"category": "compute"})
    assert r.status_code == 200
    assert all(item["category"] == "compute" for item in r.json())


def test_resources_filter_by_environment_case_insensitive():
    r = client.get("/api/resources", params={"environment": "PRODUCTION"})
    assert r.status_code == 200
    assert all(item["environment"] == "production" for item in r.json())


def test_resources_filter_by_service_case_insensitive():
    r = client.get("/api/resources", params={"service": "eks"})
    assert r.status_code == 200
    body = r.json()
    assert len(body) > 0
    assert all(item["service"] == "EKS" for item in body)


def test_insights_endpoint():
    r = client.get("/api/insights")
    assert r.status_code == 200
    body = r.json()
    assert "summary" in body
    assert isinstance(body["insights"], list)
    assert len(body["insights"]) > 0

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_api_lakehouse_stats():
    res = client.get("/api/v1/lakehouse/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "stats" in data
    assert "total_fact_rows" in data["stats"]

def test_api_dashboard_overview():
    res = client.get("/api/v1/dashboard/overview")
    assert res.status_code == 200
    data = res.json()
    assert len(data["kpis"]) == 4
    assert len(data["monthly_trend"]) > 0
    assert len(data["category_breakdown"]) > 0
    assert len(data["regional_breakdown"]) > 0
    assert data["query_latency_ms"] < 100.0

def test_api_natural_language_query():
    payload = {
        "question": "Ventas y margen de ganancia por categoría en 2025"
    }
    res = client.post("/api/v1/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["row_count"] > 0
    assert "data" in data
    assert data["latency_ms"] < 100.0

def test_api_report_generate():
    payload = {
        "question": "Top 5 regiones con mayor facturación"
    }
    res = client.post("/api/v1/report/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["kpi_cards"]) == 4
    assert len(data["highlights"]) > 0
    assert len(data["recommendations"]) > 0
    assert len(data["table_data"]) > 0

def test_api_blocks_sql_injection():
    payload = {
        "question": "test",
        "custom_sql": "DROP TABLE fact_sales;"
    }
    res = client.post("/api/v1/query", json=payload)
    assert res.status_code == 400
    assert "Query validation rejected" in res.json()["detail"]

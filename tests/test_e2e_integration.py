import pytest
from fastapi.testclient import TestClient
from src.api.server import app
from src.reporting.report_generator import StandaloneHtmlReportGenerator

client = TestClient(app)

def test_standalone_html_report_generator():
    """Verify HTML report generator produces valid HTML with luxury dark styles."""
    sample_data = {
        "headline": "Informe de Ventas Q3",
        "summary": "Resumen ejecutivo generado con IA",
        "kpi_cards": [
            {"label": "Ventas", "value": "$10,000", "change": "+5%"}
        ],
        "highlights": ["Hallazgo clave"],
        "recommendations": ["Recomendación estratégica"],
        "table_data": [
            {"categoria": "Cloud", "total": 10000}
        ],
        "sql": "SELECT * FROM fact_sales;",
        "latency_ms": 32.5
    }
    html = StandaloneHtmlReportGenerator.generate_html(sample_data)
    assert "<!DOCTYPE html>" in html
    assert "Informe de Ventas Q3" in html
    assert "Nexus BI Engine" in html
    assert "$10,000" in html

def test_api_export_html_endpoint():
    """Verify /api/v1/report/export-html returns valid text/html response."""
    payload = {
        "question": "Ventas y margen por categoría en 2025"
    }
    res = client.post("/api/v1/report/export-html", json=payload)
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "<!DOCTYPE html>" in res.text
    assert "Informe Ejecutivo:" in res.text

def test_e2e_lakehouse_query_pipeline():
    """End-to-end flow test: verifying data flow from Lakehouse to API and executive insights."""
    # 1. Check stats
    stats_res = client.get("/api/v1/lakehouse/stats")
    assert stats_res.status_code == 200
    
    # 2. Query in natural language
    query_res = client.post("/api/v1/query", json={"question": "Top 5 regiones con mayor facturacion"})
    assert query_res.status_code == 200
    data = query_res.json()
    assert data["row_count"] > 0
    assert data["latency_ms"] < 100.0
    
    # 3. Generate report
    rep_res = client.post("/api/v1/report/generate", json={"question": "Top 5 regiones con mayor facturacion"})
    assert rep_res.status_code == 200
    report = rep_res.json()
    assert len(report["kpi_cards"]) == 4
    assert len(report["highlights"]) > 0

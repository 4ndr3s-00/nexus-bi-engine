import pytest
from src.ai_engine.text_to_sql import text_to_sql
from src.ai_engine.insight_generator import insight_generator

def test_point_query_month_2_in_ai():
    """
    Test exact user case: 'Cuanto se gano el mes 2 en el sector de IA'
    Must filter d.month = 2 AND p.category = 'AI & Intelligence',
    target metric total_profit, and return a single concrete answer.
    """
    q = "Cuanto se gano el mes 2 en el sector de IA"
    res = text_to_sql.execute_analytical_query(q)
    
    assert res["is_out_of_domain"] is False
    assert "d.month = 2" in res["sql"]
    assert "p.category = 'AI & Intelligence'" in res["sql"]
    assert res["row_count"] == 1
    assert res["latency_ms"] < 120.0  # Cold start allowance
    
    report = insight_generator.generate_report(res)
    assert report["chart_type"] == "point_spotlight"
    assert report["direct_answer"] is not None
    assert "$" in report["direct_answer"]
    assert "ganancia neta obtenida fue de" in report["summary"]

def test_month_by_name_query():
    """Test Spanish month name: 'Ventas en febrero en Cloud Infrastructure'."""
    q = "Ventas en febrero en Cloud Infrastructure"
    res = text_to_sql.execute_analytical_query(q)
    assert res["is_out_of_domain"] is False
    assert "d.month = 2" in res["sql"]
    assert "p.category = 'Cloud Infrastructure'" in res["sql"]

def test_quarter_query():
    """Test Quarter extraction: 'Ganancia neta en el Q3 en LATAM'."""
    q = "Ganancia neta en el Q3 en LATAM"
    res = text_to_sql.execute_analytical_query(q)
    assert res["is_out_of_domain"] is False
    assert "d.quarter = 3" in res["sql"]
    assert "c.region = 'LATAM'" in res["sql"]

def test_comparison_query():
    """Test Comparison: 'Compara ventas de North America vs Europe'."""
    q = "Compara ventas de North America vs Europe"
    res = text_to_sql.execute_analytical_query(q)
    assert res["is_out_of_domain"] is False
    assert "c.region" in res["sql"]
    report = insight_generator.generate_report(res)
    assert report["chart_type"] in ["bar_comparison", "general_bars"]

def test_ranking_top_query():
    """Test Ranking: 'Top 3 clientes con mayor facturacion'."""
    q = "Top 3 clientes con mayor facturacion"
    res = text_to_sql.execute_analytical_query(q)
    assert res["is_out_of_domain"] is False
    assert "LIMIT 3" in res["sql"]
    assert "DESC" in res["sql"]
    assert "c.customer_name" in res["sql"]

def test_ranking_worst_polarity():
    """Test Worst Ranking: 'Los 2 sectores con peor margen'."""
    q = "Los 2 sectores con peor margen"
    res = text_to_sql.execute_analytical_query(q)
    assert res["is_out_of_domain"] is False
    assert "ASC" in res["sql"]
    assert "LIMIT 2" in res["sql"]
    report = insight_generator.generate_report(res)
    assert "menor desempeño" in report["summary"] or "Desempeño Crítico" in report["headline"]

def test_trend_query():
    """Test Time-Series Trend: 'Evolucion mensual de facturacion'."""
    q = "Evolucion mensual de facturacion"
    res = text_to_sql.execute_analytical_query(q)
    assert res["is_out_of_domain"] is False
    assert "d.month" in res["sql"]
    report = insight_generator.generate_report(res)
    assert report["chart_type"] == "time_series"

def test_compound_filter_query():
    """Test Compound Filters: 'Ventas en LATAM a traves de Cloud Marketplace'."""
    q = "Ventas en LATAM a traves de Cloud Marketplace"
    res = text_to_sql.execute_analytical_query(q)
    assert res["is_out_of_domain"] is False
    assert "c.region = 'LATAM'" in res["sql"]
    assert "ch.channel_name = 'Cloud Marketplace'" in res["sql"]

def test_out_of_domain_rrhh_rejected():
    """Verify out-of-domain HR questions are strictly rejected without hallucination."""
    q = "Cuantos empleados tiene el departamento de recursos humanos"
    res = text_to_sql.execute_analytical_query(q)
    assert res["is_out_of_domain"] is True
    assert res["sql"] == ""
    assert res["row_count"] == 0
    report = insight_generator.generate_report(res)
    assert report["chart_type"] == "out_of_domain"
    assert "no se encuentra en la base de datos" in report["summary"].lower()

def test_out_of_domain_crypto_rejected():
    """Verify out-of-domain Crypto questions are strictly rejected without hallucination."""
    q = "Cual es el precio de bitcoin hoy"
    res = text_to_sql.execute_analytical_query(q)
    assert res["is_out_of_domain"] is True
    assert res["sql"] == ""
    report = insight_generator.generate_report(res)
    assert report["chart_type"] == "out_of_domain"
    assert "bitcoin" in report["summary"].lower()

def test_out_of_domain_warehouse_stock_rejected():
    """Verify warehouse stock inventory questions are rejected without hallucination."""
    q = "Cuanto inventario queda en el almacen"
    res = text_to_sql.execute_analytical_query(q)
    assert res["is_out_of_domain"] is True
    assert res["sql"] == ""
    report = insight_generator.generate_report(res)
    assert report["chart_type"] == "out_of_domain"

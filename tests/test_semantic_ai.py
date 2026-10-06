import pytest
from src.semantic.compressor import compressor
from src.ai_engine.query_validator import guard, QueryValidationError
from src.ai_engine.text_to_sql import text_to_sql
from src.ai_engine.insight_generator import insight_generator

def test_semantic_compressor_token_efficiency():
    """Verify that semantic compressed context is ultra-compact (< 400 tokens)."""
    context = compressor.get_compressed_context()
    est_tokens = compressor.estimate_token_count()
    assert est_tokens < 400
    assert "KIMBALL STAR SCHEMA" in context
    assert "fact_sales" in context
    assert "net_revenue" in context

def test_query_guard_blocks_mutations_and_injections():
    """Verify that QueryGuard strictly rejects malicious or mutating SQL commands."""
    dangerous_queries = [
        "DROP TABLE fact_sales;",
        "DELETE FROM dim_customer WHERE 1=1;",
        "UPDATE dim_product SET list_price = 0;",
        "CREATE TABLE hack AS SELECT 1;",
        "SELECT * FROM fact_sales; DROP TABLE dim_date;",
        "INSERT INTO fact_sales VALUES (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1);",
        "PRAGMA memory_limit='1GB';",
    ]
    for q in dangerous_queries:
        with pytest.raises(QueryValidationError):
            guard.validate_and_sanitize(q)

def test_text_to_sql_and_insights_generation():
    """Verify end-to-end natural language query compilation, execution and executive insight generation."""
    question = "Muestra las ventas y margen por categoría en el año 2025"
    result = text_to_sql.execute_analytical_query(question)
    
    assert result["row_count"] > 0
    assert result["latency_ms"] < 100.0  # Ultra fast SLA
    assert "total_revenue" in result["data"][0]
    
    report = insight_generator.generate_report(result)
    assert len(report["kpi_cards"]) == 4
    assert len(report["highlights"]) > 0
    assert len(report["recommendations"]) > 0
    assert report["headline"].startswith("Informe Ejecutivo:")

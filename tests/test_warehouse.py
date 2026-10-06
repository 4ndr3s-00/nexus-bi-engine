import time
import pytest
from src.warehouse.engine import warehouse
from src.ingestion.pipeline import pipeline

def test_medallion_pipeline_execution():
    """Verify Bronze -> Silver -> Gold pipeline completes cleanly."""
    result = pipeline.run_pipeline(n_rows=50_000)
    assert result["status"] == "success"
    assert result["rows_processed"] == 50_000
    assert result["stats"]["total_fact_rows"] >= 50_000

def test_star_schema_integrity():
    """Verify that dimension and fact tables maintain relational integrity and correct counts."""
    stats = warehouse.get_stats()
    assert "dim_date" in stats["tables"]
    assert "dim_product" in stats["tables"]
    assert "dim_customer" in stats["tables"]
    assert "dim_channel" in stats["tables"]
    assert "fact_sales" in stats["tables"]
    
    assert stats["tables"]["dim_date"] == 730
    assert stats["tables"]["dim_product"] > 0
    assert stats["tables"]["dim_customer"] == 2000
    assert stats["tables"]["dim_channel"] == 4

def test_complex_olap_query_speed():
    """
    Verify complex analytical multi-join and multi-aggregate query executes in under 100ms.
    """
    sql = """
    SELECT
        d.year,
        d.quarter,
        p.category,
        c.region,
        COUNT(f.transaction_id) AS total_orders,
        ROUND(SUM(f.net_revenue), 2) AS total_revenue,
        ROUND(SUM(f.profit_margin), 2) AS total_profit,
        ROUND(AVG(f.profit_margin_pct), 2) AS avg_margin_pct
    FROM fact_sales f
    JOIN dim_date d ON f.date_id = d.date_id
    JOIN dim_product p ON f.product_id = p.product_id
    JOIN dim_customer c ON f.customer_id = c.customer_id
    WHERE d.year = 2025
      AND p.category IN ('AI & Intelligence', 'Cloud Infrastructure')
      AND c.region IN ('North America', 'Europe')
    GROUP BY 1, 2, 3, 4
    ORDER BY total_revenue DESC;
    """
    
    start = time.perf_counter()
    results = warehouse.execute_query(sql)
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    assert len(results) > 0
    # Strict speed SLA: under 100ms
    assert elapsed_ms < 100.0, f"Query took {elapsed_ms:.2f}ms, exceeding 100ms limit"

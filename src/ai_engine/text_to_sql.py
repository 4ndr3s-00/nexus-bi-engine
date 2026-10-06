import time
from typing import Optional
from src.warehouse.engine import warehouse
from src.semantic.catalog import catalog
from src.semantic.compressor import compressor
from src.semantic.domain_guard import domain_guard
from src.ai_engine.query_validator import guard, QueryValidationError
from src.ai_engine.query_classifier import QueryClassifier, QueryIntent, AnalyticalIntent

class TextToSqlEngine:
    """
    High-precision deterministic Text-to-SQL compiler with strict zero-hallucination guards.
    Handles point queries, comparisons, rankings, time-series trends and threshold diagnostics.
    """
    def __init__(self):
        self.catalog = catalog
        self.compressor = compressor

    def generate_sql_from_intent(self, intent: AnalyticalIntent) -> str:
        # Build SELECT dimensions
        dim_select = ",\n    ".join(intent.group_by)
        group_idx = ", ".join([str(i + 1) for i in range(len(intent.group_by))])

        # Build WHERE clauses
        where_parts = []
        for col, val in intent.filters.items():
            if isinstance(val, str):
                where_parts.append(f"{col} = '{val}'")
            else:
                where_parts.append(f"{col} = {val}")

        where_sql = f"\nWHERE {' AND '.join(where_parts)}" if where_parts else ""

        # Map target metric to column name in SELECT
        metric_col_map = {
            "total_profit": "total_profit",
            "net_revenue": "total_revenue",
            "margin_pct": "margin_pct",
            "total_orders": "total_orders",
            "avg_order_value": "avg_order_value"
        }
        order_col = metric_col_map.get(intent.target_metric, "total_revenue")

        sql = f"""SELECT
    {dim_select},
    COUNT(f.transaction_id) AS total_orders,
    ROUND(SUM(f.net_revenue), 2) AS total_revenue,
    ROUND(SUM(f.profit_margin), 2) AS total_profit,
    ROUND((SUM(f.profit_margin) / NULLIF(SUM(f.net_revenue), 0)) * 100, 2) AS margin_pct,
    ROUND(AVG(f.net_revenue), 2) AS avg_order_value
{self.catalog.TABLE_JOINS.strip()}{where_sql}
GROUP BY {group_idx}
ORDER BY {order_col} {intent.polarity}
LIMIT {intent.limit};"""
        return sql

    def execute_analytical_query(self, question: str, custom_sql: Optional[str] = None) -> dict:
        """
        Executes query with domain boundary validation:
        1. Checks Domain Guard against out-of-domain entities (RRHH, crypto, warehouse, etc.).
        2. Classifies intent into point, ranking, comparison, trend, etc.
        3. Compiles to deterministic ANSI SQL.
        4. Validates via zero-trust QueryGuard (EXPLAIN dry-run).
        5. Executes against DuckDB Lakehouse.
        """
        t0 = time.perf_counter()

        # Step 1: Rigid Domain Boundary Guard Check
        if not custom_sql:
            guard_check = domain_guard.check_domain_boundary(question)
            if not guard_check.is_valid:
                latency_ms = round((time.perf_counter() - t0) * 1000, 2)
                return {
                    "is_out_of_domain": True,
                    "reason": guard_check.reason,
                    "question": question,
                    "sql": "",
                    "latency_ms": latency_ms,
                    "row_count": 0,
                    "data": [],
                    "intent": None
                }

        # Step 2: Intent Classification & SQL Generation
        if custom_sql:
            sql = custom_sql
            intent = None
        else:
            intent = QueryClassifier.classify(question)
            sql = self.generate_sql_from_intent(intent)

        # Step 3: Zero-Trust Security Sandbox Validation
        validated_sql = guard.validate_and_sanitize(sql)

        # Step 4: DuckDB Execution
        results = warehouse.execute_query(validated_sql)
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        return {
            "is_out_of_domain": False,
            "question": question,
            "sql": validated_sql,
            "latency_ms": latency_ms,
            "row_count": len(results),
            "data": results,
            "intent": intent.__dict__ if intent else None
        }

text_to_sql = TextToSqlEngine()

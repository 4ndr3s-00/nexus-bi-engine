import time
import re
from typing import Optional
from src.warehouse.engine import warehouse
from src.semantic.catalog import catalog
from src.semantic.compressor import compressor
from src.ai_engine.query_validator import guard, QueryValidationError

class TextToSqlEngine:
    """
    Translates natural language analytical questions into deterministic,
    high-precision ANSI SQL queries against the Gold layer.
    """
    def __init__(self):
        self.catalog = catalog
        self.compressor = compressor

    def generate_sql(self, question: str) -> str:
        """
        Translates natural language to verified SQL using semantic pattern matching
        and dimension inference.
        """
        q = question.lower()

        # 1. Detect Dimensions
        selected_dims = []
        group_by_cols = []
        order_col = "total_revenue"

        if any(w in q for w in ["categoria", "categoría", "sector", "rubro", "producto"]):
            selected_dims.append("p.category")
            group_by_cols.append("p.category")
        if any(w in q for w in ["subcategoria", "subcategoría", "linea", "solucion"]):
            selected_dims.append("p.subcategory")
            group_by_cols.append("p.subcategory")
        if any(w in q for w in ["region", "región", "territorio", "geografia"]):
            selected_dims.append("c.region")
            group_by_cols.append("c.region")
        if any(w in q for w in ["segmento", "segment"]):
            selected_dims.append("c.segment")
            group_by_cols.append("c.segment")
        if any(w in q for w in ["canal", "channel"]):
            selected_dims.append("ch.channel_name")
            group_by_cols.append("ch.channel_name")
        if any(w in q for w in ["año", "year", "anual"]):
            selected_dims.append("d.year")
            group_by_cols.append("d.year")
        if any(w in q for w in ["trimestre", "quarter", "q1", "q2", "q3", "q4"]):
            if "d.year" not in selected_dims:
                selected_dims.append("d.year")
                group_by_cols.append("d.year")
            selected_dims.append("d.quarter")
            group_by_cols.append("d.quarter")
        if any(w in q for w in ["mes", "month", "mensual"]):
            if "d.year" not in selected_dims:
                selected_dims.append("d.year")
                group_by_cols.append("d.year")
            selected_dims.append("d.month")
            selected_dims.append("d.month_name")
            group_by_cols.append("d.month")
            group_by_cols.append("d.month_name")

        # Default fallback dimension if none mentioned
        if not selected_dims:
            selected_dims = ["p.category"]
            group_by_cols = ["p.category"]

        # 2. Detect Filters (WHERE clause)
        where_clauses = []
        if "2025" in q:
            where_clauses.append("d.year = 2025")
        elif "2026" in q:
            where_clauses.append("d.year = 2026")

        for reg in ["North America", "Europe", "LATAM", "Asia-Pacific", "Middle East"]:
            if reg.lower() in q:
                where_clauses.append(f"c.region = '{reg}'")

        for cat in ["Cloud Infrastructure", "AI & Intelligence", "CyberSecurity", "Data Engineering", "Enterprise SaaS", "Developer Platform"]:
            if cat.lower() in q or ("ai" in q.split() and cat == "AI & Intelligence"):
                where_clauses.append(f"p.category = '{cat}'")
                break

        # 3. Detect Limit
        limit = 10
        limit_match = re.search(r"top\s+(\d+)", q)
        if limit_match:
            limit = int(limit_match.group(1))

        # 4. Construct SQL
        where_sql = f"\nWHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        dim_select = ",\n    ".join(selected_dims)
        group_sql = ", ".join([str(i + 1) for i in range(len(group_by_cols))])

        sql = f"""SELECT
    {dim_select},
    COUNT(f.transaction_id) AS total_orders,
    ROUND(SUM(f.net_revenue), 2) AS total_revenue,
    ROUND(SUM(f.profit_margin), 2) AS total_profit,
    ROUND((SUM(f.profit_margin) / NULLIF(SUM(f.net_revenue), 0)) * 100, 2) AS margin_pct,
    ROUND(AVG(f.net_revenue), 2) AS avg_order_value
{self.catalog.TABLE_JOINS.strip()}{where_sql}
GROUP BY {group_sql}
ORDER BY total_revenue DESC
LIMIT {limit};"""
        return sql

    def execute_analytical_query(self, question: str, custom_sql: Optional[str] = None) -> dict:
        """
        Processes a natural language query end-to-end:
        1. Compiles question to SQL.
        2. Validates security sandbox via QueryGuard.
        3. Executes against DuckDB OLAP engine.
        4. Captures execution latency and results.
        """
        sql = custom_sql or self.generate_sql(question)
        validated_sql = guard.validate_and_sanitize(sql)

        start_time = time.perf_counter()
        results = warehouse.execute_query(validated_sql)
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "question": question,
            "sql": validated_sql,
            "latency_ms": latency_ms,
            "row_count": len(results),
            "data": results,
        }

text_to_sql = TextToSqlEngine()

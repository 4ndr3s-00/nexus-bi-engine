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
    Handles clinical healthcare domain queries across 8 EPS/IPS (Triage, Camas, Glosas, Citas)
    and B2B queries with sub-50ms execution in DuckDB.
    """
    def __init__(self):
        self.catalog = catalog
        self.compressor = compressor

    def generate_sql_from_intent(self, intent: AnalyticalIntent) -> str:
        if intent.domain == "HEALTHCARE":
            return self._generate_healthcare_sql(intent)
        return self._generate_b2b_sql(intent)

    def _generate_healthcare_sql(self, intent: AnalyticalIntent) -> str:
        sub = intent.healthcare_subdomain or "URGENCIAS"
        group_by = intent.group_by or ["i.nombre_ips"]
        dim_select = ",\n    ".join(group_by)
        group_idx = ", ".join([str(i + 1) for i in range(len(group_by))])

        # Build WHERE parts
        where_parts = []
        for col, val in intent.filters.items():
            if col == "f.servicio_like":
                where_parts.append(f"f.servicio LIKE '%{val}%'")
            elif isinstance(val, bool):
                where_parts.append(f"{col} = {str(val).lower()}")
            elif isinstance(val, (int, float)):
                where_parts.append(f"{col} = {val}")
            else:
                where_parts.append(f"{col} = '{val}'")

        where_sql = f"\nWHERE {' AND '.join(where_parts)}" if where_parts else ""

        if sub == "URGENCIAS":
            order_col = "tiempo_espera_promedio_min"
            if intent.target_metric == "total_atenciones_urgencias":
                order_col = "total_atenciones"
            elif intent.target_metric == "tasa_reingreso_72h":
                order_col = "tasa_reingreso_pct"
            elif intent.target_metric == "estancia_promedio_horas":
                order_col = "estancia_promedio_horas"

            sql = f"""SELECT
    {dim_select},
    COUNT(f.admission_id) AS total_atenciones,
    ROUND(AVG(f.tiempo_espera_minutos), 1) AS tiempo_espera_promedio_min,
    ROUND(AVG(f.tiempo_estancia_horas), 1) AS estancia_promedio_horas,
    SUM(CASE WHEN f.reingreso_72h THEN 1 ELSE 0 END) AS total_reingresos_72h,
    ROUND(SUM(CASE WHEN f.reingreso_72h THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(f.admission_id), 0), 2) AS tasa_reingreso_pct
{self.catalog.JOINS_URGENCIAS.strip()}{where_sql}
GROUP BY {group_idx}
ORDER BY {order_col} {intent.polarity}
LIMIT {intent.limit};"""
            return sql

        elif sub == "CAMAS":
            sql = f"""SELECT
    {dim_select},
    SUM(f.camas_totales) AS total_camas_instaladas,
    SUM(f.camas_ocupadas) AS total_camas_ocupadas,
    ROUND(AVG(f.tasa_ocupacion_pct), 2) AS tasa_ocupacion_pct
{self.catalog.JOINS_CAMAS.strip()}{where_sql}
GROUP BY {group_idx}
ORDER BY tasa_ocupacion_pct {intent.polarity}
LIMIT {intent.limit};"""
            return sql

        elif sub == "GLOSAS":
            sql = f"""SELECT
    {dim_select},
    ROUND(SUM(f.valor_radicado), 2) AS total_radicado,
    ROUND(SUM(f.valor_glosado), 2) AS total_glosado,
    ROUND(SUM(f.valor_levantado), 2) AS total_levantado,
    ROUND((SUM(f.valor_glosado) / NULLIF(SUM(f.valor_radicado), 0)) * 100, 2) AS tasa_glosa_pct
{self.catalog.JOINS_GLOSAS.strip()}{where_sql}
GROUP BY {group_idx}
ORDER BY total_glosado {intent.polarity}
LIMIT {intent.limit};"""
            return sql

        else:  # CITAS
            sql = f"""SELECT
    {dim_select},
    COUNT(f.cita_id) AS total_citas_solicitadas,
    ROUND(AVG(f.dias_oportunidad), 1) AS oportunidad_promedio_dias,
    ROUND(SUM(CASE WHEN f.cumple_meta_normativa THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(f.cita_id), 0), 2) AS cumplimiento_meta_pct
{self.catalog.JOINS_CITAS.strip()}{where_sql}
GROUP BY {group_idx}
ORDER BY oportunidad_promedio_dias {intent.polarity}
LIMIT {intent.limit};"""
            return sql

    def _generate_b2b_sql(self, intent: AnalyticalIntent) -> str:
        dim_select = ",\n    ".join(intent.group_by)
        group_idx = ", ".join([str(i + 1) for i in range(len(intent.group_by))])

        where_parts = []
        for col, val in intent.filters.items():
            if isinstance(val, str):
                where_parts.append(f"{col} = '{val}'")
            else:
                where_parts.append(f"{col} = {val}")

        where_sql = f"\nWHERE {' AND '.join(where_parts)}" if where_parts else ""

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
        1. Checks Domain Guard against PII violations and out-of-domain entities.
        2. Classifies intent into healthcare clinical or B2B analytical intent.
        3. Compiles to deterministic ANSI SQL for DuckDB.
        4. Validates via zero-trust QueryGuard (EXPLAIN dry-run).
        5. Executes against DuckDB Lakehouse in <50ms.
        """
        t0 = time.perf_counter()

        # Step 1: Rigid Domain Boundary Guard Check
        if not custom_sql:
            guard_check = domain_guard.check_domain_boundary(question)
            if not guard_check.is_valid:
                latency_ms = round((time.perf_counter() - t0) * 1000, 2)
                return {
                    "is_out_of_domain": True,
                    "is_pii_violation": guard_check.is_pii_violation,
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

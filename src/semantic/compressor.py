import json
from src.semantic.catalog import catalog

class SemanticCompressor:
    """
    Compresses the 8 EPS/IPS Healthcare Star Schema into a dense, token-efficient
    semantic representation (< 280 tokens).
    Prevents LLM hallucinations while preserving full relational precision across:
    Triage Manchester, ICU Beds, Glosas RIPS, and Appointment Access.
    """
    def __init__(self, cat=catalog):
        self.catalog = cat

    def get_compressed_healthcare_context(self) -> str:
        """
        Returns a compact semantic prompt describing healthcare metrics, dimensions and canonical joins.
        """
        metrics = [f"{k}={v.sql_formula}" for k, v in self.catalog.HEALTHCARE_METRICS.items()]
        dims = [f"{v.table}.{v.column}" for v in self.catalog.HEALTHCARE_DIMENSIONS.values()]

        compressed = f"""[HEALTHCARE KIMBALL STAR SCHEMA - 8 EPS/IPS 24/7]
METRICS: {', '.join(metrics)}
DIMENSIONS: {', '.join(dims)}
FACTS:
1. fact_urgencias_triage f JOIN dim_ips i ON f.ips_id=i.ips_id JOIN dim_eps e ON f.eps_id=e.eps_id JOIN dim_cie10 c ON f.cie10_code=c.cie10_code
2. fact_censo_camas f JOIN dim_ips i ON f.ips_id=i.ips_id
3. fact_auditoria_glosas f JOIN dim_ips i ON f.ips_id=i.ips_id JOIN dim_eps e ON f.eps_id=e.eps_id
4. fact_citas_oportunidad f JOIN dim_ips i ON f.ips_id=i.ips_id
RULES: Read-only SELECT. Group by sede/EPS/servicio. Zero individual patient PII (Habeas Data Ley 1581).
"""
        return compressed.strip()

    def get_compressed_retail_context(self) -> str:
        """Compact semantic prompt for retail/b2b warehouse schema."""
        metrics = [f"{k}={v.sql_formula}" for k, v in self.catalog.METRICS.items()]
        dims = [f"{v.table[4:]}.{v.column}" for v in self.catalog.DIMENSIONS.values()]
        compressed = f"""[KIMBALL STAR SCHEMA - RETAIL]
METRICS: {', '.join(metrics)}
DIMENSIONS: {', '.join(dims)}
JOINS: fact_sales f JOIN dim_date d ON f.date_id=d.date_id JOIN dim_product p ON f.product_id=p.product_id JOIN dim_customer c ON f.customer_id=c.customer_id JOIN dim_channel ch ON f.channel_id=ch.channel_id
RULES: Read-only SELECT. Group by dimensions, order by net_revenue/total_profit DESC.
"""
        return compressed.strip()

    def get_compressed_context(self, domain: str = "retail") -> str:
        """Compact semantic prompt for specified domain (< 300 tokens)."""
        if domain == "healthcare":
            return self.get_compressed_healthcare_context()
        return self.get_compressed_retail_context()

    def estimate_token_count(self, domain: str = "retail") -> int:
        """Rough estimation of token count (~4 characters per token)."""
        text = self.get_compressed_context(domain)
        return len(text) // 4

compressor = SemanticCompressor()

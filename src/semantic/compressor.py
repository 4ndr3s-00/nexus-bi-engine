import json
from src.semantic.catalog import catalog

class SemanticCompressor:
    """
    Compresses the Data Warehouse schema and business metric catalog into a
    dense, token-efficient semantic representation (< 300 tokens).
    Prevents LLM hallucinations while preserving full relational precision.
    """
    def __init__(self, cat=catalog):
        self.catalog = cat

    def get_compressed_context(self) -> str:
        """
        Returns a compact semantic prompt describing metrics, dimensions and canonical join paths.
        """
        metrics = [f"{k}={v.sql_formula}" for k, v in self.catalog.METRICS.items()]
        dims = [f"{v.table[4:]}.{v.column}" for v in self.catalog.DIMENSIONS.values()]

        compressed = f"""[KIMBALL STAR SCHEMA]
METRICS: {', '.join(metrics)}
DIMENSIONS: {', '.join(dims)}
JOINS: fact_sales f JOIN dim_date d ON f.date_id=d.date_id JOIN dim_product p ON f.product_id=p.product_id JOIN dim_customer c ON f.customer_id=c.customer_id JOIN dim_channel ch ON f.channel_id=ch.channel_id
RULES: Read-only SELECT. Group by dimensions, order by net_revenue/total_profit DESC.
"""
        return compressed.strip()

    def estimate_token_count(self) -> int:
        """Rough estimation of token count (~4 characters per token)."""
        text = self.get_compressed_context()
        return len(text) // 4

compressor = SemanticCompressor()

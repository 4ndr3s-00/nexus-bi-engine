from dataclasses import dataclass, field
from typing import Optional

@dataclass
class MetricDefinition:
    name: str
    display_name: str
    sql_formula: str
    description: str
    unit: str = "USD"
    format_type: str = "currency"  # currency, percentage, integer, float

@dataclass
class DimensionDefinition:
    table: str
    column: str
    display_name: str
    data_type: str
    description: str
    sample_values: list[str] = field(default_factory=list)

class SemanticCatalog:
    """
    Official Business Intelligence Semantic Catalog.
    Contains verified mathematical definitions of metrics and dimensional hierarchies.
    Eliminates AI hallucinations by serving as the Single Source of Truth (SSOT).
    """
    METRICS = {
        "net_revenue": MetricDefinition(
            name="net_revenue",
            display_name="Ingresos Netos",
            sql_formula="ROUND(SUM(f.net_revenue), 2)",
            description="Ingresos brutos descontando promociones y deducciones comerciales.",
            unit="$",
            format_type="currency"
        ),
        "total_profit": MetricDefinition(
            name="total_profit",
            display_name="Beneficio / Margen Neto",
            sql_formula="ROUND(SUM(f.profit_margin), 2)",
            description="Margen operativo total después de deducir el costo base.",
            unit="$",
            format_type="currency"
        ),
        "profit_margin_pct": MetricDefinition(
            name="profit_margin_pct",
            display_name="Margen de Ganancia (%)",
            sql_formula="ROUND((SUM(f.profit_margin) / NULLIF(SUM(f.net_revenue), 0)) * 100, 2)",
            description="Porcentaje del beneficio respecto a los ingresos netos.",
            unit="%",
            format_type="percentage"
        ),
        "total_orders": MetricDefinition(
            name="total_orders",
            display_name="Volumen de Pedidos",
            sql_formula="COUNT(f.transaction_id)",
            description="Número total de transacciones registradas.",
            unit="órdenes",
            format_type="integer"
        ),
        "average_order_value": MetricDefinition(
            name="average_order_value",
            display_name="Ticket Promedio (AOV)",
            sql_formula="ROUND(AVG(f.net_revenue), 2)",
            description="Valor promedio facturado por orden de compra.",
            unit="$",
            format_type="currency"
        ),
        "total_units": MetricDefinition(
            name="total_units",
            display_name="Unidades Vendidas",
            sql_formula="SUM(f.quantity)",
            description="Cantidad total de unidades o licencias comercializadas.",
            unit="unidades",
            format_type="integer"
        ),
    }

    DIMENSIONS = {
        # Time
        "year": DimensionDefinition("dim_date", "year", "Año", "INTEGER", "Año del evento (ej: 2025, 2026)", ["2025", "2026"]),
        "quarter": DimensionDefinition("dim_date", "quarter", "Trimestre", "INTEGER", "Trimestre fiscal (1 a 4)", ["1", "2", "3", "4"]),
        "month": DimensionDefinition("dim_date", "month", "Mes Numérico", "INTEGER", "Mes del año (1 a 12)", ["1", "6", "12"]),
        "month_name": DimensionDefinition("dim_date", "month_name", "Nombre del Mes", "VARCHAR", "Mes en texto", ["January", "June", "December"]),
        
        # Product
        "category": DimensionDefinition("dim_product", "category", "Categoría de Producto", "VARCHAR", "Sector tecnológico principal", 
                                       ["Cloud Infrastructure", "AI & Intelligence", "CyberSecurity", "Data Engineering", "Enterprise SaaS", "Developer Platform"]),
        "subcategory": DimensionDefinition("dim_product", "subcategory", "Subcategoría", "VARCHAR", "Línea de solución", 
                                          ["LLM Inference API", "Compute Nodes", "Zero Trust Gateway", "Streaming Pipeline"]),
        "product_name": DimensionDefinition("dim_product", "product_name", "Producto Específico", "VARCHAR", "Nombre del SKU comercial"),

        # Customer & Region
        "region": DimensionDefinition("dim_customer", "region", "Región Geográfica", "VARCHAR", "Territorio del cliente", 
                                     ["North America", "Europe", "LATAM", "Asia-Pacific", "Middle East"]),
        "segment": DimensionDefinition("dim_customer", "segment", "Segmento Comercial", "VARCHAR", "Tamaño del cliente", 
                                      ["Enterprise Global", "Mid-Market", "Scale-Up", "Public Sector"]),
        "country": DimensionDefinition("dim_customer", "country", "País", "VARCHAR", "País de facturación", ["United States", "Germany"]),

        # Channel
        "channel_name": DimensionDefinition("dim_channel", "channel_name", "Canal de Venta", "VARCHAR", "Canal de comercialización", 
                                            ["Direct Enterprise Sales", "Cloud Marketplace", "Global Partner Network", "Self-Serve Portal"]),
    }

    TABLE_JOINS = """
    FROM fact_sales f
    JOIN dim_date d ON f.date_id = d.date_id
    JOIN dim_product p ON f.product_id = p.product_id
    JOIN dim_customer c ON f.customer_id = c.customer_id
    JOIN dim_channel ch ON f.channel_id = ch.channel_id
    """

catalog = SemanticCatalog()

from dataclasses import dataclass, field
from typing import Optional, Dict

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
    Official Healthcare & Business Intelligence Semantic Catalog.
    Contains verified mathematical definitions of metrics and dimensional hierarchies
    for the 8 EPS/IPS hospital network and analytical lakehouse.
    Eliminates AI hallucinations by serving as the Single Source of Truth (SSOT).
    """
    HEALTHCARE_METRICS = {
        "tiempo_espera_promedio": MetricDefinition(
            name="tiempo_espera_promedio",
            display_name="Tiempo de Espera Promedio en Triage",
            sql_formula="ROUND(AVG(f.tiempo_espera_minutos), 1)",
            description="Tiempo medio transcurrido entre el ingreso y la atención médica según Manchester.",
            unit="minutos",
            format_type="float"
        ),
        "tasa_ocupacion_uci": MetricDefinition(
            name="tasa_ocupacion_uci",
            display_name="Tasa de Ocupación UCI",
            sql_formula="ROUND(AVG(f.tasa_ocupacion_pct), 2)",
            description="Porcentaje promedio de camas UCI ocupadas frente a capacidad instalada.",
            unit="%",
            format_type="percentage"
        ),
        "total_glosas_retenidas": MetricDefinition(
            name="total_glosas_retenidas",
            display_name="Total Glosas Retenidas",
            sql_formula="ROUND(SUM(f.valor_glosado), 2)",
            description="Monto financiero objetado por las EPS en la auditoría de cuentas médicas.",
            unit="COP",
            format_type="currency"
        ),
        "porcentaje_glosas": MetricDefinition(
            name="porcentaje_glosas",
            display_name="Tasa de Glosa (%)",
            sql_formula="ROUND((SUM(f.valor_glosado) / NULLIF(SUM(f.valor_radicado), 0)) * 100, 2)",
            description="Porcentaje del valor glosado respecto al valor total radicado.",
            unit="%",
            format_type="percentage"
        ),
        "oportunidad_citas_promedio": MetricDefinition(
            name="oportunidad_citas_promedio",
            display_name="Oportunidad de Citas Médicas",
            sql_formula="ROUND(AVG(f.dias_oportunidad), 1)",
            description="Días promedio transcurridos entre la solicitud y la asignación de la cita médica.",
            unit="días",
            format_type="float"
        ),
        "tasa_cumplimiento_citas": MetricDefinition(
            name="tasa_cumplimiento_citas",
            display_name="Cumplimiento Meta Normativa Citas",
            sql_formula="ROUND(SUM(CASE WHEN f.cumple_meta_normativa THEN 1 ELSE 0 END) * 100.0 / COUNT(f.cita_id), 2)",
            description="Porcentaje de citas asignadas dentro del plazo estándar fijado por la Supersalud.",
            unit="%",
            format_type="percentage"
        ),
        "total_atenciones_urgencias": MetricDefinition(
            name="total_atenciones_urgencias",
            display_name="Total Atenciones en Urgencias",
            sql_formula="COUNT(f.admission_id)",
            description="Número de pacientes admitidos en el servicio de urgencias.",
            unit="pacientes",
            format_type="integer"
        ),
        "tasa_reingreso_72h": MetricDefinition(
            name="tasa_reingreso_72h",
            display_name="Tasa de Reingreso Urgencias a 72h",
            sql_formula="ROUND(SUM(CASE WHEN f.reingreso_72h THEN 1 ELSE 0 END) * 100.0 / COUNT(f.admission_id), 2)",
            description="Porcentaje de pacientes que reingresan a urgencias dentro de las 72 horas del egreso.",
            unit="%",
            format_type="percentage"
        )
    }

    HEALTHCARE_DIMENSIONS = {
        "ips_nombre": DimensionDefinition("dim_ips", "nombre_ips", "Nombre de la Sede IPS", "VARCHAR", "Sede hospitalaria o centro ambulatorio"),
        "ips_24h": DimensionDefinition("dim_ips", "es_24h", "Atención 24 Horas", "BOOLEAN", "Indica si la IPS opera 24/7 de forma ininterrumpida"),
        "ips_ciudad": DimensionDefinition("dim_ips", "ciudad", "Ciudad de la Sede", "VARCHAR", "Ubicación geográfica de la IPS"),
        "eps_nombre": DimensionDefinition("dim_eps", "nombre_eps", "Aseguradora EPS", "VARCHAR", "Entidad Promotora de Salud responsable"),
        "triage_level": DimensionDefinition("fact_urgencias_triage", "triage_level", "Nivel Triage Manchester", "INTEGER", "Clasificación clínica de 1 (Crítico) a 5 (No urgente)"),
        "cie10_code": DimensionDefinition("dim_cie10", "cie10_code", "Código CIE-10", "VARCHAR", "Clasificación Internacional de Enfermedades"),
        "cie10_desc": DimensionDefinition("dim_cie10", "descripcion", "Diagnóstico Clínico", "VARCHAR", "Descripción médica del diagnóstico"),
        "servicio_camas": DimensionDefinition("fact_censo_camas", "servicio", "Servicio Hospitalario", "VARCHAR", "Área de hospitalización (UCI, Urgencias, etc.)"),
        "especialidad_citas": DimensionDefinition("fact_citas_oportunidad", "especialidad", "Especialidad Médica", "VARCHAR", "Especialidad de la consulta externa")
    }

    # B2B & General metrics for backwards compatibility
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

    # Healthcare Joins
    JOINS_URGENCIAS = """
    FROM fact_urgencias_triage f
    JOIN dim_ips i ON f.ips_id = i.ips_id
    JOIN dim_eps e ON f.eps_id = e.eps_id
    JOIN dim_cie10 c ON f.cie10_code = c.cie10_code
    JOIN dim_date d ON f.date_id = d.date_id
    """

    JOINS_CAMAS = """
    FROM fact_censo_camas f
    JOIN dim_ips i ON f.ips_id = i.ips_id
    JOIN dim_date d ON f.date_id = d.date_id
    """

    JOINS_GLOSAS = """
    FROM fact_auditoria_glosas f
    JOIN dim_ips i ON f.ips_id = i.ips_id
    JOIN dim_eps e ON f.eps_id = e.eps_id
    JOIN dim_date d ON f.date_id = d.date_id
    """

    JOINS_CITAS = """
    FROM fact_citas_oportunidad f
    JOIN dim_ips i ON f.ips_id = i.ips_id
    JOIN dim_date d ON f.date_id = d.date_id
    """

catalog = SemanticCatalog()

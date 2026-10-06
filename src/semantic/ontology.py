"""
Ontological Knowledge Graph for Nexus BI Lakehouse.
Provides strict vocabulary grounding, canonical mapping and entity definitions.
Eliminates out-of-domain hallucinations by establishing strict schema boundaries.
"""

# Canonical Entities & Synonyms
ONTOLOGY = {
    "categories": {
        "Cloud Infrastructure": [
            "cloud", "nube", "infraestructura", "compute", "almacenamiento", "storage",
            "kubernetes", "nodos", "servidores", "infrastructure"
        ],
        "AI & Intelligence": [
            "ai", "ia", "inteligencia artificial", "artificial intelligence", "llm",
            "modelos", "inferencia", "machine learning", "embeddings", "agentes"
        ],
        "CyberSecurity": [
            "ciberseguridad", "seguridad", "security", "zero trust", "firewall",
            "endpoint", "siem", "identidad", "cyber"
        ],
        "Data Engineering": [
            "datos", "data", "ingenieria de datos", "data engineering", "lakehouse",
            "pipeline", "etl", "streaming", "catalog", "big data"
        ],
        "Enterprise SaaS": [
            "saas", "software", "crm", "erp", "enterprise", "facturacion", "billing",
            "compliance"
        ],
        "Developer Platform": [
            "developers", "desarrolladores", "devops", "ci/cd", "apm", "observabilidad",
            "herramientas de desarrollo", "api management", "plataforma"
        ]
    },
    "regions": {
        "North America": ["norteamerica", "norte america", "north america", "usa", "eeuu", "estados unidos", "canada"],
        "Europe": ["europa", "europe", "ue", "alemania", "germany", "espana", "francia"],
        "LATAM": ["latam", "latinoamerica", "latino america", "sudamerica", "mexico", "brasil", "colombia", "argentina"],
        "Asia-Pacific": ["apac", "asia", "asia pacific", "asia pacifico", "japon", "china", "singapur"],
        "Middle East": ["medio oriente", "middle east", "oriente medio", "dubai", "emiratos"]
    },
    "channels": {
        "Direct Enterprise Sales": ["directo", "direct sales", "ventas directas", "corporativo directo"],
        "Cloud Marketplace": ["marketplace", "cloud marketplace", "aws marketplace", "azure marketplace"],
        "Global Partner Network": ["partners", "canal de partners", "resellers", "distribuidores"],
        "Self-Serve Portal": ["self serve", "autoservicio", "portal web", "self-service", "inbound"]
    },
    "segments": {
        "Enterprise Global": ["enterprise", "grandes empresas", "corporativo global", "enterprise global"],
        "Mid-Market": ["mid market", "medianas empresas", "mid-market"],
        "Scale-Up": ["scale up", "scaleup", "startups avanzadas"],
        "Public Sector": ["sector publico", "public sector", "gobierno"]
    },
    "months": {
        1: ["enero", "january", "mes 1", "mes uno", "primer mes"],
        2: ["febrero", "february", "mes 2", "mes dos", "segundo mes"],
        3: ["marzo", "march", "mes 3", "mes tres", "tercer mes"],
        4: ["abril", "april", "mes 4", "mes cuatro", "cuarto mes"],
        5: ["mayo", "may", "mes 5", "mes cinco", "quinto mes"],
        6: ["junio", "june", "mes 6", "mes seis", "sexto mes"],
        7: ["julio", "july", "mes 7", "mes siete", "septimo mes"],
        8: ["agosto", "august", "mes 8", "mes ocho", "octavo mes"],
        9: ["septiembre", "setiembre", "september", "mes 9", "mes nueve", "noveno mes"],
        10: ["octubre", "october", "mes 10", "mes diez", "decimo mes"],
        11: ["noviembre", "november", "mes 11", "mes once"],
        12: ["diciembre", "december", "mes 12", "mes doce", "ultimo mes"]
    },
    "quarters": {
        1: ["q1", "primer trimestre", "primer cuarto", "trimestre 1", "t1"],
        2: ["q2", "segundo trimestre", "segundo cuarto", "trimestre 2", "t2"],
        3: ["q3", "tercer trimestre", "tercer cuarto", "trimestre 3", "t3"],
        4: ["q4", "cuarto trimestre", "cuarto cuarto", "trimestre 4", "t4"]
    },
    "years": {
        2025: ["2025", "año pasado", "ano pasado", "primer año"],
        2026: ["2026", "este año", "este ano", "segundo año", "año actual"]
    },
    "metrics": {
        "total_profit": ["ganancia", "gano", "ganó", "utilidad", "beneficio", "beneficios", "ganancias", "profit", "net profit"],
        "net_revenue": ["venta", "ventas", "vendio", "vendió", "facturacion", "facturó", "facturo", "ingreso", "ingresos", "revenue"],
        "margin_pct": ["margen", "rentabilidad", "porcentaje de margen", "margin", "margen de ganancia"],
        "total_orders": ["pedidos", "ordenes", "órdenes", "transacciones", "compras", "volumen de pedidos", "orders"],
        "avg_order_value": ["ticket promedio", "promedio por venta", "aov", "valor promedio"]
    }
}

# Known out-of-domain keywords that definitively do not belong to Lakehouse data
OUT_OF_DOMAIN_BLACKLIST = {
    "recursos humanos", "rrhh", "empleados", "salarios", "nomina", "nómina", "contrataciones",
    "despidos", "vacaciones", "bitcoin", "crypto", "criptomonedas", "ethereum", "token",
    "almacen", "almacén", "bodega", "stock de inventario", "envios fisicos", "logistica de camiones",
    "visitas web", "clics", "impresiones de google", "redes sociales seguidores", "instagram likes",
    "acciones en bolsa", "dividendos de wall street", "clima", "temperatura", "medico", "pacientes"
}

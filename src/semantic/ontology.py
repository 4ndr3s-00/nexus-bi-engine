"""
Ontological Knowledge Graph for Nexus BI Lakehouse & 8 EPS/IPS Healthcare Network.
Provides strict vocabulary grounding, canonical mapping and clinical entity definitions.
Eliminates hallucinations by establishing strict schema boundaries and Habeas Data protections.
"""

ONTOLOGY = {
    # 1. Healthcare Canonical Entities (Exact match to dim_ips and dim_eps)
    "ips": {
        "Hospital Universitario Central": [
            "hospital universitario central", "hospital universitario", "huc", 
            "universitario central", "bogota 24h", "hospital central"
        ],
        "Clínica Pediátrica Santa María": [
            "clinica pediatrica santa maria", "clínica pediátrica santa maría", 
            "santa maria", "santa maría", "pediatrica santa maria", "pediatrica", "medellin 24h"
        ],
        "Hospital Traumatológico del Norte": [
            "hospital traumatologico del norte", "hospital traumatológico del norte", 
            "traumatologico del norte", "traumatológico del norte", "traumatologico", 
            "traumatológico", "hospital traumatologico", "cali 24h"
        ],
        "Clínica Metropolitana Sur": [
            "clinica metropolitana sur", "clínica metropolitana sur", "metropolitana sur", 
            "clinica sur", "clínica sur", "metropolitana", "barranquilla 24h"
        ],
        "Centro Médico Ambulatorio Chapinero": [
            "centro medico ambulatorio chapinero", "centro médico ambulatorio chapinero", 
            "ambulatorio chapinero", "chapinero"
        ],
        "IPS Especializada Poblado": [
            "ips especializada poblado", "especializada poblado", "poblado"
        ],
        "Unidad de Atención Básica Teusaquillo": [
            "unidad de atencion basica teusaquillo", "unidad de atención básica teusaquillo", 
            "atencion basica teusaquillo", "teusaquillo"
        ],
        "Policlínica Ambulatoria Occidente": [
            "policlinica ambulatoria occidente", "policlínica ambulatoria occidente", 
            "ambulatoria occidente", "occidente"
        ],
        # Aliases & common synonyms
        "Clínica Norte 24H": ["clinica norte", "clínica norte", "norte 24h"],
        "Hospital San Vicente de Paul": ["san vicente", "san vicente de paul"],
        "Centro Ambulatorio Especializado Sur": ["ambulatorio sur", "especializado sur"]
    },
    "eps": {
        "Sura EPS": ["sura", "epssura", "seguros sura"],
        "Sanitas EPS": ["sanitas", "eps sanitas", "colsanitas"],
        "Nueva EPS": ["nueva eps", "nuevaeps"],
        "Salud Total EPS": ["salud total", "saludtotal"],
        "Compensar EPS": ["compensar"],
        "Famisanar EPS": ["famisanar"],
        "Coosalud EPS": ["coosalud"],
        "Mutual Ser EPS": ["mutual ser", "mutualser"]
    },
    "triage_levels": {
        1: ["triage 1", "triage i", "resucitacion", "resucitación", "reanimacion", "reanimación", "triage rojo"],
        2: ["triage 2", "triage ii", "emergencia", "triage naranja"],
        3: ["triage 3", "triage iii", "triage amarillo"],
        4: ["triage 4", "triage iv", "urgencia menor", "triage verde"],
        5: ["triage 5", "triage v", "no urgente", "triage azul"]
    },
    "servicios_camas": {
        "UCI Adulto": ["uci adulto", "cuidados intensivos adultos", "uci adultos", "uci general"],
        "UCI Pediátrica": ["uci pediatrica", "uci pediátrica", "cuidados intensivos niños", "uci neonatal"],
        "Urgencias": ["camas urgencias", "observacion", "observación urgencias", "camas de urgencias"],
        "Hospitalización General": ["hospitalizacion general", "hospitalización general", "piso"]
    },
    "especialidades": {
        "Medicina General": ["medicina general", "medico general"],
        "Cardiología": ["cardiologia", "cardiología", "cardiólogo", "cardiologo"],
        "Pediatría": ["pediatria", "pediatría", "pediatra"],
        "Medicina Interna": ["medicina interna", "internista"],
        "Ginecología": ["ginecologia", "ginecología", "ginecologo", "obstetricia"],
        "Ortopedia": ["ortopedia", "traumatologia", "traumatología"]
    },
    "cie10": {
        "J069": ["infeccion respiratoria", "ira", "resfriado", "j069"],
        "I10": ["hipertension", "hipertensión", "presion alta", "i10"],
        "E119": ["diabetes", "glicemia", "e119"],
        "J189": ["neumonia", "neumonía", "pulmonia", "j189"],
        "K358": ["apendicitis", "apendicectomia", "k358"],
        "R104": ["dolor abdominal", "abdomen agudo", "r104"]
    },
    "healthcare_metrics": {
        "estancia_promedio_horas": [
            "estancia", "media de estancia", "estancia media", "tiempo de estancia", 
            "horas de estancia", "duracion de estancia", "duración de estancia", "dias de estancia"
        ],
        "tiempo_espera_minutos": [
            "tiempo de espera", "espera promedio", "minutos de espera", "triage tiempo", 
            "espera en urgencias", "cuanto tardan", "cuánto tardan"
        ],
        "tasa_ocupacion_pct": [
            "ocupacion", "ocupación", "camas uci", "censo de camas", "camas ocupadas", 
            "porcentaje de ocupacion", "saturacion de camas"
        ],
        "valor_glosado": [
            "glosas", "glosado", "valor glosado", "glosa rips", "cobros objetados", 
            "glosas retenidas", "porcentaje de glosas"
        ],
        "dias_oportunidad": [
            "oportunidad de citas", "oportunidad", "dias de oportunidad", "días de oportunidad", 
            "tiempo de espera cita", "asignacion de citas", "dias para cita"
        ],
        "reingreso_72h": [
            "reingreso", "reingresos a 72 horas", "tasa de reingreso", "reingresos 72h"
        ],
        "total_atenciones": [
            "atenciones", "volumen de atenciones", "pacientes atendidos", "urgencias atendidas", 
            "total de urgencias", "admisiones"
        ]
    },

    # 2. Tech B2B Historical Entities (Preserved for backwards compatibility)
    "categories": {
        "Cloud Infrastructure": ["cloud", "nube", "infraestructura", "compute", "almacenamiento", "storage", "kubernetes", "nodos", "servidores"],
        "AI & Intelligence": ["ai", "ia", "inteligencia artificial", "artificial intelligence", "llm", "modelos", "inferencia", "machine learning"],
        "CyberSecurity": ["ciberseguridad", "seguridad", "security", "zero trust", "firewall", "endpoint", "siem"],
        "Data Engineering": ["datos", "data", "ingenieria de datos", "data engineering", "lakehouse", "pipeline", "etl", "big data"],
        "Enterprise SaaS": ["saas", "software", "crm", "erp", "enterprise", "facturacion", "billing"],
        "Developer Platform": ["developers", "desarrolladores", "devops", "ci/cd", "apm", "observabilidad"]
    },
    "regions": {
        "North America": ["norteamerica", "norte america", "north america", "usa", "eeuu", "estados unidos", "canada"],
        "Europe": ["europa", "europe", "ue", "alemania", "germany", "espana", "francia"],
        "LATAM": ["latam", "latinoamerica", "latino america", "sudamerica", "mexico", "brasil", "colombia", "argentina"],
        "Asia-Pacific": ["apac", "asia", "asia pacific", "asia pacifico", "japon", "china"],
        "Middle East": ["medio oriente", "middle east", "oriente medio", "dubai"]
    },
    "channels": {
        "Direct Enterprise Sales": ["directo", "direct sales", "ventas directas", "corporativo directo"],
        "Cloud Marketplace": ["marketplace", "cloud marketplace", "aws marketplace"],
        "Global Partner Network": ["partners", "canal de partners", "resellers", "distribuidores"],
        "Self-Serve Portal": ["self serve", "autoservicio", "portal web", "self-service"]
    },
    "segments": {
        "Enterprise Global": ["enterprise", "grandes empresas", "corporativo global"],
        "Mid-Market": ["mid market", "medianas empresas", "mid-market"],
        "Scale-Up": ["scale up", "scaleup", "startups avanzadas"],
        "Public Sector": ["sector publico", "public sector", "gobierno"]
    },

    # 3. Temporal Dimensions
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

OUT_OF_DOMAIN_BLACKLIST = {
    "recursos humanos", "rrhh", "empleados", "salarios", "nomina", "nómina", "contrataciones",
    "despidos", "vacaciones", "bitcoin", "crypto", "criptomonedas", "ethereum", "token",
    "almacen", "almacén", "bodega", "stock de inventario", "envios fisicos", "logistica de camiones",
    "visitas web", "clics", "impresiones de google", "redes sociales seguidores", "instagram likes",
    "acciones en bolsa", "dividendos de wall street", "clima", "temperatura"
}

PII_KEYWORDS = {
    "cedula", "cédula", "nombre del paciente", "quien es el paciente", "quién es el paciente",
    "identificacion del paciente", "identificación del paciente", "numero de documento",
    "número de documento", "historia clinica de", "historia clínica de", "direccion del paciente",
    "dirección del paciente", "telefono del paciente", "teléfono del paciente"
}

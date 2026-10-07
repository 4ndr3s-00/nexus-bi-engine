import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Any
from src.semantic.ontology import ONTOLOGY

class QueryIntent(str, Enum):
    POINT = "POINT"                  # Exact single value/filter
    COMPARISON = "COMPARISON"        # Comparison between 2+ entities
    RANKING = "RANKING"              # Top/Bottom N
    TREND = "TREND"                  # Time evolution
    THRESHOLD = "THRESHOLD"          # Values meeting condition
    GENERAL = "GENERAL"              # General aggregation

@dataclass
class AnalyticalIntent:
    intent_type: QueryIntent
    domain: str = "HEALTHCARE"          # "HEALTHCARE" or "B2B"
    healthcare_subdomain: Optional[str] = None  # "URGENCIAS", "CAMAS", "GLOSAS", "CITAS"
    target_metric: str = "tiempo_espera_minutos"
    polarity: str = "DESC"              # DESC or ASC
    filters: dict[str, Any] = field(default_factory=dict)
    group_by: list[str] = field(default_factory=list)
    limit: int = 10
    threshold_clause: Optional[str] = None
    entities_mentioned: list[str] = field(default_factory=list)

class QueryClassifier:
    """
    Advanced Semantic Classifier for Multi-Intent Analytics.
    Dissects natural language questions into precise query components for:
    1. 8 EPS/IPS Healthcare Network (Urgencias Triage, Camas UCI, Glosas, Oportunidad de Citas).
    2. B2B Commercial & Tech categories.
    """
    @classmethod
    def classify(cls, question: str) -> AnalyticalIntent:
        q = question.lower()
        entities = []
        filters = {}
        group_by = []

        # -------------------------------------------------------------
        # 1. DOMAIN IDENTIFICATION (HEALTHCARE vs B2B)
        # -------------------------------------------------------------
        has_hc_keyword = bool(re.search(
            r"\b(triage|urgencias|cama|camas|uci|glosa|glosas|rips|eps|ips|hospital|clinica|clínica|médica|medica|cita|citas|reingreso|cie10|cie-10|pacientes)\b",
            q
        ))

        is_healthcare = (
            any(any(s in q for s in syns) for syns in ONTOLOGY["ips"].values()) or
            any(any(s in q for s in syns) for syns in ONTOLOGY["eps"].values()) or
            any(any(s in q for s in syns) for syns in ONTOLOGY["triage_levels"].values()) or
            any(any(s in q for s in syns) for syns in ONTOLOGY["servicios_camas"].values()) or
            any(any(s in q for s in syns) for syns in ONTOLOGY["especialidades"].values()) or
            any(any(s in q for s in syns) for syns in ONTOLOGY["cie10"].values()) or
            any(any(s in q for s in syns) for syns in ONTOLOGY["healthcare_metrics"].values()) or
            has_hc_keyword
        )

        domain = "HEALTHCARE" if is_healthcare else "B2B"

        # Determine Polarity (Best vs Worst / Highest vs Lowest)
        is_bottom = any(w in q for w in ["peor", "peores", "menor", "menores", "bajo", "bajos", "menos", "minimo", "mínimo", "bottom", "worst", "lowest"])
        polarity = "ASC" if is_bottom else "DESC"

        # Extract Common Temporal Filters (Month, Quarter, Year)
        detected_month = None
        for m_num, m_syns in ONTOLOGY["months"].items():
            for syn in m_syns:
                if re.search(rf"\b{re.escape(syn)}\b", q):
                    detected_month = m_num
                    entities.append(f"month:{m_num}")
                    break
            if detected_month:
                break
        if not detected_month:
            m_match = re.search(r"\bmes\s+(\d+)\b", q)
            if m_match:
                val = int(m_match.group(1))
                if 1 <= val <= 12:
                    detected_month = val
                    entities.append(f"month:{val}")
        if detected_month:
            filters["d.month"] = detected_month

        for y_num, y_syns in ONTOLOGY["years"].items():
            if any(syn in q for syn in y_syns):
                filters["d.year"] = y_num
                entities.append(f"year:{y_num}")
                break

        # -------------------------------------------------------------
        # 2. HEALTHCARE DOMAIN CLASSIFICATION
        # -------------------------------------------------------------
        if domain == "HEALTHCARE":
            subdomain = "URGENCIAS"  # default clinical subdomain
            target_metric = "tiempo_espera_promedio"

            # Check 24H filter
            if any(w in q for w in ["24h", "24 horas", "sedes 24h", "hospitales 24 horas", "atencion continua"]):
                filters["i.es_24h"] = True
                entities.append("filter:es_24h")

            # Check IPS
            for ips_name, ips_syns in ONTOLOGY["ips"].items():
                if any(syn in q for syn in ips_syns):
                    filters["i.nombre_ips"] = ips_name
                    entities.append(f"ips:{ips_name}")
                    break

            # Check EPS
            for eps_name, eps_syns in ONTOLOGY["eps"].items():
                if any(syn in q for syn in eps_syns):
                    filters["e.nombre_eps"] = eps_name
                    entities.append(f"eps:{eps_name}")
                    break

            # Check Triage Level
            for t_level, t_syns in ONTOLOGY["triage_levels"].items():
                for syn in t_syns:
                    if re.search(rf"\b{re.escape(syn)}\b", q):
                        filters["f.triage_level"] = t_level
                        entities.append(f"triage:{t_level}")
                        break
                if "f.triage_level" in filters:
                    break

            # Check Especialidad Citas
            for esp_name, esp_syns in ONTOLOGY["especialidades"].items():
                if any(syn in q for syn in esp_syns):
                    filters["f.especialidad"] = esp_name
                    entities.append(f"especialidad:{esp_name}")
                    subdomain = "CITAS"
                    target_metric = "oportunidad_citas_promedio"
                    break

            # Check Subdomain: Camas / UCI
            if any(w in q for w in ["cama", "camas", "censo", "ocupacion", "ocupación", "saturacion"]) or re.search(r"\buci\b", q):
                subdomain = "CAMAS"
                target_metric = "tasa_ocupacion_uci"
                if any(w in q for w in ["uci adulto", "uci adultos"]):
                    filters["f.servicio"] = "UCI Adulto"
                elif any(w in q for w in ["uci pediatrica", "uci pediátrica", "neonatal"]):
                    filters["f.servicio"] = "UCI Pediátrica"
                elif re.search(r"\buci\b", q):
                    filters["f.servicio_like"] = "UCI"

            # Check Subdomain: Glosas
            elif any(w in q for w in ["glosa", "glosas", "rips", "objetado", "facturacion medica", "cuentas medicas"]):
                subdomain = "GLOSAS"
                target_metric = "total_glosas_retenidas"

            # Check Subdomain: Citas
            elif any(w in q for w in ["cita", "citas", "consulta externa", "oportunidad", "asignacion"]):
                subdomain = "CITAS"
                target_metric = "oportunidad_citas_promedio"

            # Check Subdomain: Urgencias / Triage
            elif any(w in q for w in ["triage", "urgencias", "espera", "reingreso", "manchester"]):
                subdomain = "URGENCIAS"
                if any(w in q for w in ["reingreso", "reingresos"]):
                    target_metric = "tasa_reingreso_72h"
                elif any(w in q for w in ["atenciones", "volumen", "pacientes"]):
                    target_metric = "total_atenciones_urgencias"
                else:
                    target_metric = "tiempo_espera_promedio"

            # Determine Intent Type & Groupings
            if any(w in q for w in ["top", "ranking", "peor", "peores", "mayor", "mayores", "sedes con mas", "eps con mas"]):
                intent_type = QueryIntent.RANKING
            elif any(w in q for w in ["compara", "vs", "frente a", "comparativa"]):
                intent_type = QueryIntent.COMPARISON
            elif any(w in q for w in ["evolucion", "tendencia", "historico", "mes a mes"]):
                intent_type = QueryIntent.TREND
            elif any(w in q for w in ["cuanto", "cuánto", "cual es", "cuál es", "promedio"]) and ("i.nombre_ips" in filters or "e.nombre_eps" in filters):
                intent_type = QueryIntent.POINT
            else:
                intent_type = QueryIntent.GENERAL

            limit = 10
            if subdomain == "URGENCIAS":
                if any(w in q for w in ["diagnostico", "diagnósticos", "cie10", "cie-10", "enfermedad", "patologia", "patología"]):
                    group_by = ["c.cie10_code", "c.descripcion"]
                    target_metric = "total_atenciones_urgencias"
                elif "f.triage_level" in filters:
                    group_by = ["i.nombre_ips", "f.triage_level"]
                elif any(w in q for w in ["eps", "aseguradora"]):
                    group_by = ["e.nombre_eps"]
                elif any(w in q for w in ["hora", "horario", "pico"]):
                    group_by = ["f.hora_ingreso"]
                else:
                    group_by = ["i.nombre_ips", "i.es_24h"]

            elif subdomain == "CAMAS":
                if any(w in q for w in ["servicio", "area", "área"]):
                    group_by = ["i.nombre_ips", "f.servicio"]
                else:
                    group_by = ["i.nombre_ips"]

            elif subdomain == "GLOSAS":
                if any(w in q for w in ["ips", "sede", "hospital"]):
                    group_by = ["i.nombre_ips"]
                elif any(w in q for w in ["motivo", "causa", "codigo"]):
                    group_by = ["f.motivo_glosa_codigo"]
                else:
                    group_by = ["e.nombre_eps"]

            elif subdomain == "CITAS":
                if "f.especialidad" in filters:
                    group_by = ["i.nombre_ips", "f.especialidad"]
                else:
                    group_by = ["f.especialidad"]

            return AnalyticalIntent(
                intent_type=intent_type,
                domain="HEALTHCARE",
                healthcare_subdomain=subdomain,
                target_metric=target_metric,
                polarity=polarity,
                filters=filters,
                group_by=group_by,
                limit=limit,
                entities_mentioned=entities
            )

        # -------------------------------------------------------------
        # 3. B2B COMMERCIAL CLASSIFICATION (BACKWARDS COMPATIBILITY)
        # -------------------------------------------------------------
        target_metric = "net_revenue"
        for metric_name, synonyms in ONTOLOGY["metrics"].items():
            if any(s in q for s in synonyms):
                target_metric = metric_name
                entities.append(f"metric:{metric_name}")
                break

        # Detect Quarter
        detected_quarter = None
        for q_num, q_syns in ONTOLOGY["quarters"].items():
            for syn in q_syns:
                if syn in q:
                    detected_quarter = q_num
                    entities.append(f"quarter:{q_num}")
                    break
            if detected_quarter:
                break
        if detected_quarter:
            filters["d.quarter"] = detected_quarter

        # Detect Categories
        for cat_name, cat_syns in ONTOLOGY["categories"].items():
            for syn in cat_syns:
                if len(syn) <= 2:
                    if re.search(rf"\b{re.escape(syn)}\b", q):
                        filters["p.category"] = cat_name
                        entities.append(f"category:{cat_name}")
                        break
                else:
                    if syn in q:
                        filters["p.category"] = cat_name
                        entities.append(f"category:{cat_name}")
                        break
            if "p.category" in filters:
                break

        # Detect Region
        for reg_name, reg_syns in ONTOLOGY["regions"].items():
            if any(syn in q for syn in reg_syns):
                filters["c.region"] = reg_name
                entities.append(f"region:{reg_name}")
                break

        # Detect Channel
        for ch_name, ch_syns in ONTOLOGY["channels"].items():
            if any(syn in q for syn in ch_syns):
                filters["ch.channel_name"] = ch_name
                entities.append(f"channel:{ch_name}")
                break

        # Detect Segment
        for seg_name, seg_syns in ONTOLOGY["segments"].items():
            if any(syn in q for syn in seg_syns):
                filters["c.segment"] = seg_name
                entities.append(f"segment:{seg_name}")
                break

        threshold_match = re.search(r"(?:menor|mayor|inferior|superior)\s+(?:al?|de)\s+(\d+(?:\.\d+)?)\s*(%|m|k)?", q)
        if threshold_match:
            intent_type = QueryIntent.THRESHOLD
        elif any(w in q for w in ["evolucion", "evolución", "tendencia", "historico", "histórico", "mes a mes", "a lo largo"]):
            intent_type = QueryIntent.TREND
        elif any(w in q for w in ["compara", "comparar", "comparativa", " vs ", "frente a"]):
            intent_type = QueryIntent.COMPARISON
        elif any(w in q for w in ["top", "ranking", "peor", "peores", "mejor", "mejores", "primeros", "primeras", "ultimos", "últimos"]):
            intent_type = QueryIntent.RANKING
        elif detected_month is not None and "p.category" in filters:
            intent_type = QueryIntent.POINT
        elif any(w in q for w in ["cuanto", "cuánto", "cual fue", "cuál fue", "que mes", "qué mes"]) and (detected_month is not None or "d.year" in filters or "c.region" in filters):
            intent_type = QueryIntent.POINT
        else:
            intent_type = QueryIntent.GENERAL

        limit = 10
        if intent_type == QueryIntent.POINT:
            limit = 1
            if "p.category" in filters:
                group_by.append("p.category")
            if "d.month" in filters:
                group_by.extend(["d.year", "d.month", "d.month_name"])
            elif "d.year" in filters:
                group_by.append("d.year")
            if "c.region" in filters:
                group_by.append("c.region")
            if not group_by:
                group_by.append("p.category")

        elif intent_type == QueryIntent.TREND:
            group_by = ["d.year", "d.month", "d.month_name"]
            limit = 24
            polarity = "ASC"

        elif intent_type == QueryIntent.RANKING:
            r_match = re.search(r"(?:top|peores|mejores|los|las)\s+(\d+)", q)
            if not r_match:
                r_match = re.search(r"\b(\d+)\s*(?:sectores|categorias|categorías|productos|clientes|regiones|canales|meses)", q)
            limit = int(r_match.group(1)) if r_match else 5
            if any(w in q for w in ["cliente", "clientes"]):
                group_by = ["c.customer_name", "c.segment"]
            elif any(w in q for w in ["region", "regiones"]):
                group_by = ["c.region"]
            elif any(w in q for w in ["canal", "canales"]):
                group_by = ["ch.channel_name"]
            elif any(w in q for w in ["mes", "meses"]):
                group_by = ["d.year", "d.month", "d.month_name"]
            else:
                group_by = ["p.category"]

        elif intent_type == QueryIntent.COMPARISON:
            limit = 10
            if any(w in q for w in ["trimestre", "quarter", "q1", "q2", "q3", "q4"]):
                group_by = ["d.year", "d.quarter"]
            elif any(w in q for w in ["region", "regiones"]):
                group_by = ["c.region"]
            elif any(w in q for w in ["canal", "canales"]):
                group_by = ["ch.channel_name"]
            else:
                group_by = ["p.category"]

        else:
            if any(w in q for w in ["region", "regiones"]):
                group_by = ["c.region"]
            elif any(w in q for w in ["canal", "canales"]):
                group_by = ["ch.channel_name"]
            elif any(w in q for w in ["mes", "meses"]):
                group_by = ["d.year", "d.month", "d.month_name"]
            else:
                group_by = ["p.category"]

        return AnalyticalIntent(
            intent_type=intent_type,
            domain="B2B",
            target_metric=target_metric,
            polarity=polarity,
            filters=filters,
            group_by=group_by,
            limit=limit,
            entities_mentioned=entities
        )

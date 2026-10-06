import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from src.semantic.ontology import ONTOLOGY

class QueryIntent(str, Enum):
    POINT = "POINT"                  # Exact single value/filter (e.g. Month 2 in AI)
    COMPARISON = "COMPARISON"        # Comparison between 2+ items (e.g. Q1 vs Q2)
    RANKING = "RANKING"              # Top/Bottom N
    TREND = "TREND"                  # Time evolution over months/quarters
    THRESHOLD = "THRESHOLD"          # Values meeting condition (< 39%)
    GENERAL = "GENERAL"              # General aggregation

@dataclass
class AnalyticalIntent:
    intent_type: QueryIntent
    target_metric: str = "net_revenue"  # net_revenue, total_profit, margin_pct, total_orders, avg_order_value
    polarity: str = "DESC"              # DESC for best/top, ASC for worst/bottom
    filters: dict[str, any] = field(default_factory=dict)
    group_by: list[str] = field(default_factory=list)
    limit: int = 10
    threshold_clause: Optional[str] = None
    entities_mentioned: list[str] = field(default_factory=list)

class QueryClassifier:
    """
    Advanced Semantic Classifier for Multi-Intent Analytics.
    Dissects natural language questions into precise query components.
    """
    @classmethod
    def classify(cls, question: str) -> AnalyticalIntent:
        q = question.lower()
        entities = []
        filters = {}
        group_by = []

        # 1. Detect Metric Intent
        target_metric = "net_revenue"
        for metric_name, synonyms in ONTOLOGY["metrics"].items():
            if any(s in q for s in synonyms):
                target_metric = metric_name
                entities.append(f"metric:{metric_name}")
                break

        # 2. Detect Specific Month ("mes 2", "febrero", etc.)
        detected_month = None
        for m_num, m_syns in ONTOLOGY["months"].items():
            # Check exact regex pattern for "mes X" or direct month name
            for syn in m_syns:
                pattern = rf"\b{re.escape(syn)}\b"
                if re.search(pattern, q):
                    detected_month = m_num
                    entities.append(f"month:{m_num}")
                    break
            if detected_month:
                break
        
        # Also check for regex "mes (\d+)" if not found
        if not detected_month:
            m_match = re.search(r"\bmes\s+(\d+)\b", q)
            if m_match:
                val = int(m_match.group(1))
                if 1 <= val <= 12:
                    detected_month = val
                    entities.append(f"month:{val}")

        if detected_month:
            filters["d.month"] = detected_month

        # 3. Detect Quarter
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

        # 4. Detect Year
        for y_num, y_syns in ONTOLOGY["years"].items():
            if any(syn in q for syn in y_syns):
                filters["d.year"] = y_num
                entities.append(f"year:{y_num}")
                break

        # 5. Detect Categories
        for cat_name, cat_syns in ONTOLOGY["categories"].items():
            for syn in cat_syns:
                # Use word boundaries for short acronyms like "ai" or "ia"
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

        # 6. Detect Region
        for reg_name, reg_syns in ONTOLOGY["regions"].items():
            if any(syn in q for syn in reg_syns):
                filters["c.region"] = reg_name
                entities.append(f"region:{reg_name}")
                break

        # 7. Detect Channel
        for ch_name, ch_syns in ONTOLOGY["channels"].items():
            if any(syn in q for syn in ch_syns):
                filters["ch.channel_name"] = ch_name
                entities.append(f"channel:{ch_name}")
                break

        # 8. Detect Segment
        for seg_name, seg_syns in ONTOLOGY["segments"].items():
            if any(syn in q for syn in seg_syns):
                filters["c.segment"] = seg_name
                entities.append(f"segment:{seg_name}")
                break

        # 9. Determine Polarity (Best vs Worst)
        is_bottom = any(w in q for w in ["peor", "peores", "menor", "menores", "bajo", "bajos", "menos", "minimo", "mínimo", "bottom", "worst", "lowest"])
        polarity = "ASC" if is_bottom else "DESC"

        # 10. Determine Intent Type
        # Check threshold (e.g. "menor al 39%", "menos de 100m")
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
            # Point query: exact month + category (e.g. "cuanto se gano el mes 2 en el sector de IA")
            intent_type = QueryIntent.POINT
        elif any(w in q for w in ["cuanto", "cuánto", "cual fue", "cuál fue", "que mes", "qué mes"]) and (detected_month is not None or "d.year" in filters or "c.region" in filters):
            intent_type = QueryIntent.POINT
        else:
            intent_type = QueryIntent.GENERAL

        # 11. Determine Groupings & Limit based on intent
        limit = 10
        if intent_type == QueryIntent.POINT:
            limit = 1
            # For a point query, include the filtered dimensions in select
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
            polarity = "ASC"  # Chronological

        elif intent_type == QueryIntent.RANKING:
            r_match = re.search(r"(?:top|peores|mejores|los|las)\s+(\d+)", q)
            if not r_match:
                # Check for digit before noun
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

        else: # GENERAL
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
            target_metric=target_metric,
            polarity=polarity,
            filters=filters,
            group_by=group_by,
            limit=limit,
            entities_mentioned=entities
        )

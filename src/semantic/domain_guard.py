import re
from typing import Optional
from src.semantic.ontology import ONTOLOGY, OUT_OF_DOMAIN_BLACKLIST

class DomainGuardResult:
    def __init__(self, is_valid: bool, reason: Optional[str] = None, detected_ood_term: Optional[str] = None):
        self.is_valid = is_valid
        self.reason = reason
        self.detected_ood_term = detected_ood_term

class DomainGuard:
    """
    Rigid Anti-Hallucination Guard.
    Validates whether the user's question falls within the scope of the
    Lakehouse Data Warehouse (Sales, Tech Categories, B2B Clients, Channels, Time 2025-2026).
    Rejects out-of-domain entities immediately before generating SQL.
    """
    @classmethod
    def check_domain_boundary(cls, question: str) -> DomainGuardResult:
        q_lower = question.lower()

        # 1. Direct Blacklist Check
        for ood_term in OUT_OF_DOMAIN_BLACKLIST:
            pattern = rf"\b{re.escape(ood_term)}\b"
            if re.search(pattern, q_lower):
                return DomainGuardResult(
                    is_valid=False,
                    detected_ood_term=ood_term,
                    reason=(
                        f"La consulta hace referencia a '{ood_term}', que no se encuentra en la base de datos de Nexus BI. "
                        "Nuestra base de datos contiene exclusivamente registros comerciales de productos tecnológicos, "
                        "facturación B2B, canales de venta y márgenes financieros de 2025 y 2026."
                    )
                )

        # 2. Check if the question mentions at least one domain concept or metric
        has_metric = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["metrics"].values())
        has_category = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["categories"].values())
        has_region = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["regions"].values())
        has_channel = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["channels"].values())
        has_segment = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["segments"].values())
        has_time = (
            any(any(s in q_lower for s in syns) for syns in ONTOLOGY["months"].values()) or
            any(any(s in q_lower for s in syns) for syns in ONTOLOGY["quarters"].values()) or
            any(any(s in q_lower for s in syns) for syns in ONTOLOGY["years"].values()) or
            any(w in q_lower for w in ["mes", "año", "ano", "trimestre", "quarter", "tiempo", "periodo", "fecha"])
        )
        has_general_analytics = any(w in q_lower for w in ["peor", "mejor", "top", "total", "cuanto", "cuánto", "ranking", "compara", "promedio"])

        # If question is completely devoid of business dimensions or analytical intent
        if not (has_metric or has_category or has_region or has_channel or has_segment or has_time or has_general_analytics):
            return DomainGuardResult(
                is_valid=False,
                reason=(
                    "La información solicitada no se encuentra en la base de datos empresarial. "
                    "Puedes consultar sobre: Categorías tecnológicas (Cloud, IA, Ciberseguridad, Data, SaaS), "
                    "Regiones (Norteamérica, Europa, LATAM, APAC), Canales de venta, o Métricas de facturación y margen."
                )
            )

        return DomainGuardResult(is_valid=True)

domain_guard = DomainGuard()

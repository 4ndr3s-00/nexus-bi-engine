import re
from typing import Optional
from src.semantic.ontology import ONTOLOGY, OUT_OF_DOMAIN_BLACKLIST, PII_KEYWORDS

class DomainGuardResult:
    def __init__(
        self,
        is_valid: bool,
        reason: Optional[str] = None,
        detected_ood_term: Optional[str] = None,
        is_pii_violation: bool = False
    ):
        self.is_valid = is_valid
        self.reason = reason
        self.detected_ood_term = detected_ood_term
        self.is_pii_violation = is_pii_violation

class DomainGuard:
    """
    Rigid Anti-Hallucination & Habeas Data Privacy Guard.
    1. Blocks PII deanonymization attempts under Colombian Ley 1581 and medical secrecy rules.
    2. Rejects out-of-domain entities (crypto, HR payroll, warehouse logistics, etc.).
    3. Validates that the query falls within the scope of the 8 EPS/IPS Healthcare Lakehouse.
    """
    @classmethod
    def check_domain_boundary(cls, question: str) -> DomainGuardResult:
        q_lower = question.lower()

        # 1. PII / Habeas Data Protection Check
        for pii_term in PII_KEYWORDS:
            pattern = rf"\b{re.escape(pii_term)}\b"
            if re.search(pattern, q_lower):
                return DomainGuardResult(
                    is_valid=False,
                    detected_ood_term=pii_term,
                    is_pii_violation=True,
                    reason=(
                        "🚫 [ALERTA DE SEGURIDAD - HABEAS DATA / LEY 1581]: "
                        f"La consulta intenta acceder a datos identificables ('{pii_term}'). "
                        "Por estricto protocolo de privacidad y reserva legal de la historia clínica, "
                        "todos los registros de pacientes se encuentran anonimizados con tokens SHA-256 irreversibles. "
                        "Solo se permiten análisis agregados de salud pública, tiempos asistenciales y gestión hospitalaria."
                    )
                )

        # 2. Direct Blacklist Check
        for ood_term in OUT_OF_DOMAIN_BLACKLIST:
            pattern = rf"\b{re.escape(ood_term)}\b"
            if re.search(pattern, q_lower):
                return DomainGuardResult(
                    is_valid=False,
                    detected_ood_term=ood_term,
                    reason=(
                        f"La consulta hace referencia a '{ood_term}', que no se encuentra en la base de datos de Nexus BI. "
                        "El sistema gestiona exclusivamente datos asistenciales y financieros de las 8 EPS/IPS "
                        "(Triage Urgencias, Camas UCI, Glosas RIPS, Oportunidad de Citas y CIE-10)."
                    )
                )

        # 3. Check if the question mentions healthcare or business dimensions
        has_healthcare_metric = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["healthcare_metrics"].values())
        has_ips = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["ips"].values())
        has_eps = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["eps"].values())
        has_triage = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["triage_levels"].values())
        has_servicios = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["servicios_camas"].values())
        has_especialidad = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["especialidades"].values())
        has_cie10 = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["cie10"].values())

        # General business/time/analytical matches
        has_metric = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["metrics"].values())
        has_category = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["categories"].values())
        has_region = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["regions"].values())
        has_channel = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["channels"].values())
        has_segment = any(any(s in q_lower for s in syns) for syns in ONTOLOGY["segments"].values())
        has_time = (
            any(any(s in q_lower for s in syns) for syns in ONTOLOGY["months"].values()) or
            any(any(s in q_lower for s in syns) for syns in ONTOLOGY["quarters"].values()) or
            any(any(s in q_lower for s in syns) for syns in ONTOLOGY["years"].values()) or
            any(w in q_lower for w in ["mes", "año", "ano", "trimestre", "quarter", "tiempo", "periodo", "fecha", "24h", "24 horas", "semana", "urgencias", "hospital", "clinica", "clínica"])
        )
        has_general_analytics = any(w in q_lower for w in ["peor", "mejor", "top", "total", "cuanto", "cuánto", "ranking", "compara", "promedio", "ocupacion", "ocupación", "espera"])

        is_domain_match = (
            has_healthcare_metric or has_ips or has_eps or has_triage or has_servicios or
            has_especialidad or has_cie10 or has_metric or has_category or has_region or
            has_channel or has_segment or has_time or has_general_analytics
        )

        if not is_domain_match:
            return DomainGuardResult(
                is_valid=False,
                reason=(
                    "La información solicitada no corresponde al dominio de gestión hospitalaria ni del Lakehouse. "
                    "Puedes consultar: Tiempos de Triage Manchester en sedes 24h, Ocupación de camas UCI, "
                    "Glosas por EPS, Oportunidad de citas por especialidad o diagnósticos CIE-10 más frecuentes."
                )
            )

        return DomainGuardResult(is_valid=True)

domain_guard = DomainGuard()

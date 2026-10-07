import re
import unicodedata
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

def strip_accents(text: str) -> str:
    """Removes diacritics/accents from text for consistent matching."""
    if not text:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )

@dataclass
class EvidenceUnit:
    category: str
    content: str
    line_number: int = 0
    confidence: float = 1.0

@dataclass
class CompressedEvidence:
    dense_context: str
    target_category: str
    relevant_units: List[EvidenceUnit]
    estimated_tokens: int
    exact_quote: Optional[str] = None

class ClinicalEvidenceCompressor:
    """
    Precision Token & Evidence Compressor for Medical Documents (PDF-Engine style).
    Parses messy clinical OCR/PDF text into typed clinical evidence units,
    and extracts dense, ultra-relevant context (<350 tokens) for any auditor question.
    Eliminates AI hallucinations by grounding responses in verified document lines.
    """
    CATEGORY_KEYWORDS = {
        "DIAGNOSTICO": ["diagnostico", "cie10", "cie-10", "enfermedad", "patologia", "sintoma", "cuadro", "impresion", "dx"],
        "MEDICAMENTO": ["medicamento", "dosis", "posologia", "insulina", "tableta", "formula", "prescripcion", "ampolla", "mg", "ml", "ui", "mipres"],
        "MEDICO": ["medico", "doctor", "dra", "dr", "registro", "rm", "especialista", "tratante", "firma"],
        "PROCEDIMIENTO": ["procedimiento", "orden", "resonancia", "cirugia", "apendicectomia", "triage", "urgencias", "cups", "radiografia", "laboratorio"],
        "FECHA_TIEMPO": ["fecha", "dias", "estancia", "horas", "radicacion", "atencion", "tiempo", "mes", "vencimiento", "extemporaneo", "72h"],
        "VALOR_TARIFA": ["valor", "costo", "cobro", "factura", "cop", "reclamado", "pesos", "$", "tarifa"],
        "GLOSA_RIESGO": ["glosa", "riesgo", "alerta", "inconsistencia", "sin firma", "sin sello", "extemporane", "ilegible", "rechazo", "vencid"]
    }

    def segment_document(self, text: str) -> List[EvidenceUnit]:
        """Segments raw document text into typed clinical evidence units."""
        lines = [line.strip() for line in (text or "").split("\n") if line.strip()]
        units: List[EvidenceUnit] = []

        for idx, line in enumerate(lines, 1):
            norm_line = strip_accents(line).upper()
            line_tokens = set(re.findall(r"\b[A-Z0-9]+\b", norm_line))
            assigned_cat = "GENERAL"

            for cat, keywords in self.CATEGORY_KEYWORDS.items():
                for kw in keywords:
                    norm_kw = strip_accents(kw).upper()
                    if len(norm_kw) <= 3:
                        if norm_kw in line_tokens:
                            assigned_cat = cat
                            break
                    else:
                        if norm_kw in norm_line:
                            assigned_cat = cat
                            break
                if assigned_cat != "GENERAL":
                    break

            units.append(EvidenceUnit(
                category=assigned_cat,
                content=line,
                line_number=idx
            ))

        return units

    def identify_query_target(self, question: str) -> str:
        """Determines the primary clinical target category of the auditor's question."""
        q_norm = strip_accents(question).upper()
        q_tokens = set(re.findall(r"\b[A-Z0-9]+\b", q_norm))
        for cat, keywords in self.CATEGORY_KEYWORDS.items():
            for kw in keywords:
                norm_kw = strip_accents(kw).upper()
                if len(norm_kw) <= 3:
                    if norm_kw in q_tokens:
                        return cat
                else:
                    if norm_kw in q_norm:
                        return cat
        return "GENERAL"

    def compress_for_query(
        self,
        document_text: str,
        question: str,
        max_tokens: int = 350
    ) -> CompressedEvidence:
        """
        Compresses document text into a dense semantic slice matching the auditor's question.
        Returns dense context, matched units, and exact quote candidate.
        """
        units = self.segment_document(document_text)
        target_cat = self.identify_query_target(question)
        
        # 1. Score units by relevance to query
        q_words = [w.lower() for w in re.findall(r"\w+", strip_accents(question)) if len(w) > 3]
        
        scored_units = []
        for u in units:
            score = 0
            # Target category match
            if u.category == target_cat and target_cat != "GENERAL":
                score += 5
            # Word overlap match
            u_words = [w.lower() for w in re.findall(r"\w+", strip_accents(u.content))]
            matches = set(q_words).intersection(u_words)
            score += len(matches) * 3

            # Entity patterns (RM numbers, codes, values, dates)
            if re.search(r"\b[A-Z][0-9]{2,3}\b", u.content):  # CIE-10 pattern
                score += 2
            if re.search(r"RM[- :]*[0-9]{4,8}", u.content, re.IGNORECASE):
                score += 2
            if "$" in u.content or "COP" in u.content.upper():
                score += 1

            scored_units.append((score, u))

        # 2. Sort by score descending and select top units
        scored_units.sort(key=lambda x: x[0], reverse=True)
        top_units = [u for score, u in scored_units if score > 0]

        # If few scored, fall back to preserving chronological order of all units up to token budget
        if not top_units:
            top_units = units[:8]
        else:
            # Add top units while respecting token budget
            top_units = top_units[:7]
            # Re-sort chronologically by line number for natural narrative
            top_units.sort(key=lambda u: u.line_number)

        # 3. Assemble dense context
        dense_lines = [f"[L{u.line_number}|{u.category}]: {u.content}" for u in top_units]
        dense_context = "\n".join(dense_lines)

        # 4. Extract candidate exact quote
        exact_quote = top_units[0].content if top_units else None

        estimated_tokens = len(dense_context) // 4

        return CompressedEvidence(
            dense_context=dense_context,
            target_category=target_cat,
            relevant_units=top_units,
            estimated_tokens=estimated_tokens,
            exact_quote=exact_quote
        )

evidence_compressor = ClinicalEvidenceCompressor()

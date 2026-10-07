import pytest
from starlette.testclient import TestClient
from src.api.server import app
from src.strata_core.evidence_compressor import evidence_compressor
from src.strata_core.document_qa import document_qa

client = TestClient(app)

def test_evidence_compressor_segmentation_and_token_budget():
    """Verify evidence compressor segments and maintains token budget < 350 tokens."""
    sample_text = """
    HOSPITAL UNIVERSITARIO CENTRAL - NIT 890.980.123-1
    PACIENTE: HASH-PAC-001 | EDAD: 48
    DIAGNÓSTICO: I10 - HIPERTENSIÓN ESENCIAL PRIMARIA
    SERVICIO: URGENCIAS Y OBSERVACIÓN 48H
    MEDICO TRATANTE: DRA. VALENTINA MORALES VELEZ - RM-482910
    PRESCRIPCIÓN: LOSARTAN 50 MG CADA 12 HORAS
    FIRMA DIGITAL VERIFICADA | SELLO DE HABILITACIÓN ACTIVO
    VALOR RECLAMADO: $2,850,000.00 COP
    """
    units = evidence_compressor.segment_document(sample_text)
    assert len(units) >= 6
    assert any(u.category == "DIAGNOSTICO" for u in units)
    assert any(u.category == "MEDICO" for u in units)
    assert any(u.category == "MEDICAMENTO" for u in units)

    compressed = evidence_compressor.compress_for_query(
        document_text=sample_text,
        question="¿Qué medicamento y dosis se prescribió?",
        max_tokens=350
    )
    assert compressed.estimated_tokens < 350
    assert compressed.target_category == "MEDICAMENTO"
    assert "LOSARTAN" in compressed.dense_context

@pytest.mark.anyio
async def test_document_qa_direct_answers_and_exact_quotes():
    """Verify document QA engine answers questions with exact quotes and high confidence."""
    sample_text = """
    PRESCRIPCIÓN MÉDICA NO POS / MIPRES
    DIAGNÓSTICO: E119 DIABETES MELLITUS TIPO 2
    INSULINA GLARGINA 100 UI/ML
    MEDICO: DRA. CAMILA RESTREPO - RM-992144
    FIRMA DIGITAL VALIDA
    """
    metadata = {
        "cie10_code": "E119",
        "cie10_desc": "Diabetes mellitus tipo 2",
        "medico_tratante": "Dra. Camila Restrepo",
        "registro_medico": "RM-992144",
        "valor_reclamado": 185000.0,
        "riesgo_glosa_detectado": False,
        "document_type": "Fórmula Médica"
    }

    # 1. Ask about medicine
    res_med = await document_qa.ask_document(
        document_id="DOC-TEST-01",
        question="¿Qué dosis de insulina se formuló?",
        document_text=sample_text,
        metadata=metadata
    )
    assert "INSULINA GLARGINA" in res_med.answer
    assert res_med.exact_quote is not None
    assert res_med.confidence_score >= 0.95
    assert res_med.compressed_tokens < 350

    # 2. Ask about physician
    res_doc = await document_qa.ask_document(
        document_id="DOC-TEST-01",
        question="¿Quién es el médico tratante y su registro?",
        document_text=sample_text,
        metadata=metadata
    )
    assert "Dra. Camila Restrepo" in res_doc.answer
    assert "RM-992144" in res_doc.answer

def test_api_document_ask_endpoint():
    """Verify POST /api/v1/documents/{doc_id}/ask returns structured QA response."""
    payload = {"question": "¿Cuál es el diagnóstico CIE-10 del paciente?"}
    res = client.post("/api/v1/documents/DOC-2026-001/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["document_id"] == "DOC-2026-001"
    assert "I10" in data["answer"] or "Hipertensión" in data["answer"]
    assert data["exact_quote"] is not None
    assert data["confidence_score"] >= 0.95
    assert data["compressed_tokens"] < 350
    assert data["latency_ms"] < 100.0

def test_api_document_ask_not_found():
    """Verify non-existent document yields 404."""
    payload = {"question": "¿Qué diagnóstico tiene?"}
    res = client.post("/api/v1/documents/DOC-NONEXISTENT/ask", json=payload)
    assert res.status_code == 404

import pytest
from src.strata_core.client import StrataCoreClient, DocumentAuditExtraction
from src.strata_core.document_store import MedicalDocumentStore, MedicalDocumentItem

@pytest.mark.anyio
async def test_strata_core_client_health():
    client = StrataCoreClient(base_url="http://localhost:8001")
    health = await client.check_health()
    assert "status" in health
    assert "engine" in health

@pytest.mark.anyio
async def test_strata_core_client_local_evaluation():
    client = StrataCoreClient(base_url="http://localhost:8001")
    
    # 1. Normal valid document
    result = await client.evaluate_scanned_document(
        document_id="TEST-001",
        document_type="Incapacidad Médica",
        raw_text="DIAGNÓSTICO J069 INFECCIÓN RESPIRATORIA AGUDA. DR. CARLOS GOMEZ RM-882194.",
        ips_name="Hospital Universitario Central",
        eps_name="Sura EPS"
    )
    assert isinstance(result, DocumentAuditExtraction)
    assert result.diagnostico_cie10_code == "J069"
    assert result.consistencia_clinica is True
    assert result.glosa_sugerida is None

    # 2. Extemporaneous document that should trigger glosa
    result_glosa = await client.evaluate_scanned_document(
        document_id="TEST-002",
        document_type="Factura RIPS",
        raw_text="FACTURA VENCIDA RADICACION EXTEMPORANEA APENDICITIS K358",
        ips_name="Clínica Norte 24H",
        eps_name="Sanitas EPS"
    )
    assert result_glosa.diagnostico_cie10_code == "K358"
    assert result_glosa.consistencia_clinica is False
    assert result_glosa.glosa_sugerida is not None
    assert "GL-04" in result_glosa.glosa_sugerida

def test_medical_document_store():
    store = MedicalDocumentStore()
    
    # Check default seeded documents
    docs = store.list_documents()
    assert len(docs) >= 5

    # Filter by EPS
    sura_docs = store.list_documents(eps="Sura")
    assert len(sura_docs) >= 1
    assert all("sura" in d.eps_receptora.lower() for d in sura_docs)

    # Filter by status
    pendientes = store.list_documents(estado="Pendiente")
    assert len(pendientes) >= 5

    # Get single document
    doc = store.get_document("DOC-2026-001")
    assert doc is not None
    assert doc.id == "DOC-2026-001"

    # Record auditor decision: Aprobado
    updated = store.record_decision(
        doc_id="DOC-2026-001",
        decision="Aprobado",
        auditor_id="AUD-09",
        auditor_name="Dr. Juan Auditor EPS",
        observaciones="Documento verificado y coherente con soportes."
    )
    assert updated.estado == "Aprobado"
    assert len(updated.historial_auditoria) == 1
    assert updated.historial_auditoria[0].decision == "Aprobado"

    # Record glosa on DOC-2026-003
    updated_glosa = store.record_decision(
        doc_id="DOC-2026-003",
        decision="Glosado",
        auditor_id="AUD-09",
        auditor_name="Dr. Juan Auditor EPS",
        motivo_glosa="GL-04 Radicación extemporánea",
        observaciones="Supera los 30 días de radicación permitidos por Supersalud."
    )
    assert updated_glosa.estado == "Glosado"
    assert updated_glosa.historial_auditoria[0].motivo_glosa == "GL-04 Radicación extemporánea"

    # Invalid decision error test
    with pytest.raises(ValueError):
        store.record_decision(
            doc_id="DOC-2026-001",
            decision="DecisionInvalida",
            auditor_id="AUD-09",
            auditor_name="Auditor"
        )

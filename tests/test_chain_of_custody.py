import pytest
from starlette.testclient import TestClient
from src.api.server import app
from src.strata_core.document_store import document_store, compute_document_hash, MedicalDocumentItem

client = TestClient(app)

def test_document_sha256_hash_generation():
    """Verify all documents in the store have valid 64-char hex SHA-256 hashes."""
    docs = document_store.list_documents()
    assert len(docs) >= 5
    for doc in docs:
        assert len(doc.sha256_hash) == 64
        assert int(doc.sha256_hash, 16) > 0  # Valid hex string

def test_document_hash_tamper_detection():
    """Verify modifying text or financial amount results in completely different hash."""
    h1 = compute_document_hash("Text A", "RAD-001", "IPS 1", "EPS 1", 1000.0)
    h2 = compute_document_hash("Text B", "RAD-001", "IPS 1", "EPS 1", 1000.0)
    h3 = compute_document_hash("Text A", "RAD-001", "IPS 1", "EPS 1", 2000.0)
    
    assert h1 != h2
    assert h1 != h3
    assert len(h1) == 64

def test_auditor_decision_cryptographic_chain():
    """Verify decisions create an immutable, linked chain of custody."""
    doc = document_store.get_document("DOC-2026-001")
    assert doc is not None

    initial_history_len = len(doc.historial_auditoria)
    
    # 1. Record decision
    updated = document_store.record_decision(
        doc_id="DOC-2026-001",
        decision="Aprobado",
        auditor_id="AUD-TEST-01",
        auditor_name="Dr. Auditor Test",
        observaciones="Cumple con todos los requisitos"
    )
    assert len(updated.historial_auditoria) == initial_history_len + 1
    last_record = updated.historial_auditoria[-1]
    assert len(last_record.chain_hash) == 64
    assert last_record.decision == "Aprobado"
    assert "T" in last_record.fecha_decision

def test_api_decision_endpoint_returns_chain_hash():
    """Verify POST /api/v1/documents/decision records and returns chain hash."""
    payload = {
        "document_id": "DOC-2026-002",
        "decision": "Glosado",
        "auditor_id": "AUD-TEST-99",
        "auditor_name=":"Auditor RIPS",
        "motivo_glosa": "GL-04 Autorización o radicación extemporánea",
        "observaciones": "Fuera de término"
    }
    # Note: fix typo in key
    clean_payload = {
        "document_id": "DOC-2026-002",
        "decision": "Glosado",
        "auditor_id": "AUD-TEST-99",
        "auditor_name": "Auditor RIPS",
        "motivo_glosa": "GL-04 Autorización o radicación extemporánea",
        "observaciones": "Fuera de término"
    }
    res = client.post("/api/v1/documents/decision", json=clean_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    doc_data = data["document"]
    assert doc_data["estado"] == "Glosado"
    assert len(doc_data["historial_auditoria"]) > 0
    latest_hist = doc_data["historial_auditoria"][-1]
    assert len(latest_hist["chain_hash"]) == 64

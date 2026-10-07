import pytest
from starlette.testclient import TestClient
from src.api.server import app

client = TestClient(app)

def test_hospital_overview_endpoint():
    """Verify GET /api/v1/hospital/overview returns 8 EPS/IPS KPIs and clinical breakdowns."""
    response = client.get("/api/v1/hospital/overview")
    assert response.status_code == 200
    data = response.json()
    
    assert "kpis" in data
    assert len(data["kpis"]) == 4
    assert any("Triage" in k["label"] for k in data["kpis"])
    assert any("UCI" in k["label"] for k in data["kpis"])
    
    assert "triage_by_level" in data
    assert len(data["triage_by_level"]) == 5  # Manchester I to V
    
    assert "bed_occupancy_by_ips" in data
    assert len(data["bed_occupancy_by_ips"]) >= 4
    
    assert "glosas_by_eps" in data
    assert len(data["glosas_by_eps"]) >= 4
    
    assert "appointment_opportunity" in data
    assert len(data["appointment_opportunity"]) >= 4
    
    assert data["network_summary"]["operacion_24_7"] is True
    assert data["query_latency_ms"] < 100.0

def test_hospital_query_endpoint():
    """Verify POST /api/v1/hospital/query executes clinical natural language query."""
    payload = {"question": "¿Cuál es el tiempo de espera promedio en Triage en los hospitales 24 horas?"}
    response = client.post("/api/v1/hospital/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_out_of_domain"] is False
    assert "fact_urgencias_triage" in data["sql"]
    assert len(data["data"]) > 0

def test_hospital_report_endpoint():
    """Verify POST /api/v1/hospital/report returns executive clinical briefing."""
    payload = {"question": "Ocupación de camas UCI por sede hospitalaria"}
    response = client.post("/api/v1/hospital/report", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Censo Hospitalario y Capacidad" in data["headline"]
    assert len(data["kpi_cards"]) == 4
    assert len(data["highlights"]) >= 2
    assert len(data["recommendations"]) >= 1

def test_documents_pending_list_and_filter():
    """Verify GET /api/v1/documents/pending returns queue and supports filtering."""
    # 1. All pending
    res = client.get("/api/v1/documents/pending")
    assert res.status_code == 200
    data = res.json()
    assert data["total_documents"] >= 5
    assert len(data["documents"]) >= 5

    # 2. Filter by EPS
    res_eps = client.get("/api/v1/documents/pending?eps=Sura")
    assert res_eps.status_code == 200
    data_eps = res_eps.json()
    assert all("sura" in d["eps_receptora"].lower() for d in data_eps["documents"])

def test_document_detail_and_not_found():
    """Verify GET /api/v1/documents/{id}."""
    res = client.get("/api/v1/documents/DOC-2026-001")
    assert res.status_code == 200
    doc = res.json()
    assert doc["id"] == "DOC-2026-001"
    assert "RAD-COL" in doc["numero_radicado"]

    res_404 = client.get("/api/v1/documents/NON-EXISTENT")
    assert res_404.status_code == 404

def test_documents_evaluate_strata():
    """Verify POST /api/v1/documents/evaluate triggers Strata Core perception."""
    payload = {
        "document_id": "TEST-DOC-89",
        "document_type": "Factura RIPS",
        "raw_text": "DIAGNÓSTICO I10 HIPERTENSIÓN. DRA. VALENTINA MORALES RM-482910.",
        "ips_name": "Hospital Universitario Central",
        "eps_name": "Sura EPS"
    }
    res = client.post("/api/v1/documents/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["diagnostico_cie10_code"] == "I10"
    assert data["medico_tratante"] == "Dra. Valentina Morales Vélez"
    assert data["consistencia_clinica"] is True

def test_documents_decision_workflow_and_glosa_sync():
    """Verify POST /api/v1/documents/decision records auditor decision and impacts Lakehouse."""
    payload = {
        "document_id": "DOC-2026-005",
        "decision": "Glosado",
        "auditor_id": "AUD-55",
        "auditor_name": "Auditor Jefe EPS Sanitas",
        "motivo_glosa": "GL-03 Inconsistencia pertinencia médica",
        "observaciones": "Orden neurológica con diagnóstico CIE-10 abdominal no justificado."
    }
    res = client.post("/api/v1/documents/decision", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["document"]["estado"] == "Glosado"
    assert len(data["document"]["historial_auditoria"]) >= 1

def test_documents_custom_json_create():
    """Verify POST /api/v1/documents/custom creates document, runs Strata Core and queues it."""
    payload = {
        "document_type": "Factura RIPS",
        "ips_emisora": "Clínica Norte 24H",
        "eps_receptora": "Sanitas EPS",
        "valor_reclamado": 3500000.0,
        "raw_text": "DIAGNÓSTICO J069 INFECCIÓN RESPIRATORIA AGUDA. DR. CARLOS GÓMEZ RM-771829. SIN FIRMA",
        "prioridad": "Alta"
    }
    res = client.post("/api/v1/documents/custom", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    doc = data["document"]
    assert "RAD-USR" in doc["numero_radicado"]
    assert doc["is_user_uploaded"] is True
    assert doc["cie10_code"] == "J069"
    assert doc["riesgo_glosa_detectado"] is True  # Because 'SIN FIRMA' triggers glosa risk
    
    # Verify it is in the queue at the front
    pending_res = client.get("/api/v1/documents/pending")
    assert pending_res.status_code == 200
    pending_docs = pending_res.json()["documents"]
    assert any(d["id"] == doc["id"] for d in pending_docs)

def test_documents_upload_multipart_form():
    """Verify POST /api/v1/documents/upload handles multipart upload with custom text/file."""
    form_data = {
        "document_type": "Incapacidad Médica",
        "ips_emisora": "Hospital San Vicente de Paul",
        "eps_receptora": "Nueva EPS",
        "valor_reclamado": "650000.0",
        "raw_text": "INCAPACIDAD MÉDICA POR 5 DÍAS. DIAGNÓSTICO I10. DRA. VALENTINA MORALES RM-482910.",
        "prioridad": "Alta"
    }
    # Upload with a small text file
    files = {
        "file": ("incapacidad_firmada.txt", b"CERTIFICADO MEDICO FIRMADO DIGITALMENTE VALIDO", "text/plain")
    }
    res = client.post("/api/v1/documents/upload", data=form_data, files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    doc = data["document"]
    assert doc["file_name"] == "incapacidad_firmada.txt"
    assert doc["is_user_uploaded"] is True
    assert doc["cie10_code"] == "I10"


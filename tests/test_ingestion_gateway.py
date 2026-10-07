import pytest
from starlette.testclient import TestClient
from src.api.server import app
from src.ingestion.gateway import ingestion_gateway, IngestionGateway
from src.ingestion.adapters.mock_adapter import MockHospitalAdapter
from src.ingestion.adapters.rest_adapter import RestHospitalAdapter
from src.warehouse.engine import warehouse

client = TestClient(app)

def test_mock_adapter_generates_all_tables():
    """Verify MockHospitalAdapter produces conforming Polars DataFrames."""
    adapter = MockHospitalAdapter()
    dims = adapter.fetch_dimensions()
    assert "dim_ips" in dims
    assert "dim_eps" in dims
    assert len(dims["dim_ips"]) == 8
    assert len(dims["dim_eps"]) == 8

    admissions = adapter.fetch_admissions(n_rows=50, dims=dims)
    assert len(admissions) == 50
    assert "admission_id" in admissions.columns
    assert "triage_level" in admissions.columns

    beds = adapter.fetch_beds(dims=dims)
    assert len(beds) > 0
    assert "tasa_ocupacion_pct" in beds.columns

    glosas = adapter.fetch_glosas(dims=dims)
    assert len(glosas) > 0
    assert "valor_glosado" in glosas.columns

    appointments = adapter.fetch_appointments(dims=dims)
    assert len(appointments) > 0
    assert "dias_oportunidad" in appointments.columns

def test_rest_adapter_fallback_on_unreachable_api():
    """Verify RestHospitalAdapter gracefully falls back to mock when EHR is unreachable."""
    adapter = RestHospitalAdapter(base_url="http://127.0.0.1:54321/offline-ehr", timeout_sec=0.2)
    dims = adapter.fetch_dimensions()
    assert len(dims["dim_ips"]) == 8

    admissions = adapter.fetch_admissions(n_rows=20, dims=dims)
    assert len(admissions) == 20

def test_ingestion_gateway_switching_and_loading():
    """Verify IngestionGateway dynamically switches providers and loads all events."""
    gw = IngestionGateway()
    data = gw.load_all_events(n_urgencias=100, provider="mock")
    assert "dimensions" in data
    assert "facts" in data
    assert len(data["facts"]["fact_urgencias_triage"]) == 100

def test_push_ingest_hospital_events_endpoint():
    """Verify POST /api/v1/ingest/hospital-events accepts live events and syncs to Gold."""
    payload = {
        "source_system": "SAP Health HIS - Clínica Metropolitana Sur",
        "api_token": "bearer-token-live-891",
        "events": [
            {
                "event_type": "admission",
                "ips_id": 7,
                "eps_id": 2,
                "date_id": 20261007,
                "payload": {
                    "admission_id": 999901,
                    "cie10_id": 1,
                    "triage_level": 2,
                    "tiempo_espera_minutos": 14.5,
                    "tiempo_estancia_horas": 3.8,
                    "reingreso_72h": False,
                    "paciente_hash": "PAC-PUSH-TEST-01"
                }
            },
            {
                "event_type": "bed_census",
                "ips_id": 7,
                "eps_id": 2,
                "date_id": 20261007,
                "payload": {
                    "census_id": 999902,
                    "servicio": "UCI Médica",
                    "camas_totales": 20,
                    "camas_ocupadas": 17,
                    "tasa_ocupacion_pct": 85.0
                }
            },
            {
                "event_type": "glosa",
                "ips_id": 7,
                "eps_id": 2,
                "date_id": 20261007,
                "payload": {
                    "glosa_id": 999903,
                    "valor_radicado": 4500000.0,
                    "valor_glosado": 600000.0,
                    "valor_aceptado": 0.0,
                    "motivo_glosa": "GL-02 Falta firma médica",
                    "estado_glosa": "Objetada"
                }
            },
            {
                "event_type": "appointment",
                "ips_id": 7,
                "eps_id": 2,
                "date_id": 20261007,
                "payload": {
                    "cita_id": 999904,
                    "especialidad": "Pediatría",
                    "dias_oportunidad": 2,
                    "meta_normativa_dias": 3,
                    "cumple_meta_normativa": True
                }
            }
        ]
    }

    res = client.post("/api/v1/ingest/hospital-events", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["events_ingested"] == 4
    assert data["source_system"] == "SAP Health HIS - Clínica Metropolitana Sur"

    # Verify event was inserted into Gold Layer in DuckDB
    with warehouse.get_connection(read_only=True) as con:
        r = con.execute("SELECT COUNT(*) FROM fact_urgencias_triage WHERE admission_id = 999901;").fetchone()
        assert r[0] == 1

def test_push_ingest_empty_batch_rejected():
    """Verify empty events batch is rejected with 400 Bad Request."""
    payload = {
        "source_system": "Cerner HIS",
        "events": []
    }
    res = client.post("/api/v1/ingest/hospital-events", json=payload)
    assert res.status_code == 400

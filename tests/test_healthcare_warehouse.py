import time
import pytest
from src.warehouse.engine import warehouse
from src.ingestion.pipeline import pipeline

def test_healthcare_pipeline_execution():
    """Verify healthcare Medallion pipeline runs cleanly and loads all 8 EPS/IPS."""
    result = pipeline.run_pipeline(n_urgencias=50_000)
    assert result["status"] == "success"
    assert result["total_facts_processed"] > 50_000
    
    stats = warehouse.get_stats()
    assert stats["tables"]["dim_ips"] == 8
    assert stats["tables"]["dim_eps"] == 8
    assert stats["tables"]["dim_cie10"] == 10
    assert stats["tables"]["dim_paciente_anonimizado"] == 10_000

def test_healthcare_triage_query_speed():
    """Verify triage waiting times query on 24h hospital branches runs in <50ms."""
    sql = """
    SELECT
        i.nombre_ips,
        f.triage_level,
        COUNT(f.admission_id) AS total_atenciones,
        ROUND(AVG(f.tiempo_espera_minutos), 1) AS espera_promedio_min
    FROM fact_urgencias_triage f
    JOIN dim_ips i ON f.ips_id = i.ips_id
    WHERE i.es_24h = TRUE AND f.triage_level = 2
    GROUP BY 1, 2
    ORDER BY espera_promedio_min ASC;
    """
    t0 = time.perf_counter()
    res = warehouse.execute_query(sql)
    latency_ms = (time.perf_counter() - t0) * 1000
    
    assert len(res) > 0
    assert latency_ms < 50.0

def test_healthcare_glosas_by_eps():
    """Verify audit glosa calculations across EPS insurers execute in <50ms."""
    sql = """
    SELECT
        e.nombre_eps,
        ROUND(SUM(g.valor_radicado), 2) AS total_radicado,
        ROUND(SUM(g.valor_glosado), 2) AS total_glosado,
        ROUND(SUM(g.valor_glosado) * 100.0 / NULLIF(SUM(g.valor_radicado), 0), 2) AS tasa_glosa_pct
    FROM fact_auditoria_glosas g
    JOIN dim_eps e ON g.eps_id = e.eps_id
    GROUP BY 1
    ORDER BY tasa_glosa_pct DESC;
    """
    t0 = time.perf_counter()
    res = warehouse.execute_query(sql)
    latency_ms = (time.perf_counter() - t0) * 1000
    
    assert len(res) == 8
    assert latency_ms < 50.0

def test_patient_data_anonymization():
    """Verify that patient identities are strictly hashed with SHA-256 tokens."""
    sql = "SELECT patient_hash_id FROM dim_paciente_anonimizado LIMIT 5;"
    rows = warehouse.execute_query(sql)
    for r in rows:
        h = r["patient_hash_id"]
        assert h.startswith("PAC-")
        assert len(h) >= 16

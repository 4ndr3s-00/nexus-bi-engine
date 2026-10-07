import pytest
from src.ai_engine.text_to_sql import text_to_sql
from src.ai_engine.insight_generator import insight_generator

def test_healthcare_triage_24h_query():
    """Verify natural language query for triage wait times in 24h hospitals."""
    q = "¿Cuál es el tiempo de espera promedio en Triage en los hospitales 24 horas?"
    res = text_to_sql.execute_analytical_query(q)
    
    assert res["is_out_of_domain"] is False
    assert "fact_urgencias_triage" in res["sql"]
    assert "i.es_24h = true" in res["sql"]
    assert "tiempo_espera_promedio_min" in res["sql"]
    assert res["row_count"] > 0
    assert res["latency_ms"] < 120.0  # Cold start allowance (warm runs <30ms)

    report = insight_generator.generate_report(res)
    assert "Informe Asistencial de Urgencias" in report["headline"]
    assert report["direct_answer"] is not None
    assert "minutos" in report["direct_answer"]
    assert len(report["kpi_cards"]) == 4
    assert any("Triage Promedio" in card["label"] for card in report["kpi_cards"])

def test_healthcare_uci_occupancy_query():
    """Verify natural language query for UCI bed occupancy by IPS."""
    q = "Ocupación de camas UCI por sede hospitalaria"
    res = text_to_sql.execute_analytical_query(q)
    
    assert res["is_out_of_domain"] is False
    assert "fact_censo_camas" in res["sql"]
    assert "tasa_ocupacion_pct" in res["sql"]
    assert res["row_count"] > 0
    assert res["latency_ms"] < 60.0

    report = insight_generator.generate_report(res)
    assert "Censo Hospitalario y Capacidad" in report["headline"]
    assert "%" in report["direct_answer"]
    assert any("Ocupación UCI" in card["label"] for card in report["kpi_cards"])

def test_healthcare_glosas_by_eps_query():
    """Verify query for glosas by EPS."""
    q = "¿Qué EPS tiene mayor valor de glosas objetadas?"
    res = text_to_sql.execute_analytical_query(q)
    
    assert res["is_out_of_domain"] is False
    assert "fact_auditoria_glosas" in res["sql"]
    assert "total_glosado" in res["sql"]
    assert "e.nombre_eps" in res["sql"]
    assert res["row_count"] > 0

    report = insight_generator.generate_report(res)
    assert "Auditoría Médica y Glosas" in report["headline"]
    assert "$" in report["direct_answer"]
    assert any("Total Glosado" in card["label"] for card in report["kpi_cards"])

def test_healthcare_citas_oportunidad_query():
    """Verify query for appointment opportunity lead times by specialty."""
    q = "Oportunidad de citas en cardiología"
    res = text_to_sql.execute_analytical_query(q)
    
    assert res["is_out_of_domain"] is False
    assert "fact_citas_oportunidad" in res["sql"]
    assert "f.especialidad = 'Cardiología'" in res["sql"]
    assert "oportunidad_promedio_dias" in res["sql"]
    assert res["row_count"] > 0

    report = insight_generator.generate_report(res)
    assert "Oportunidad de Citas Médicas" in report["headline"]
    assert "días" in report["direct_answer"]

def test_healthcare_cie10_diagnostics_frequency():
    """Verify query for top CIE-10 diagnoses in emergencies."""
    q = "Cuáles son los diagnósticos CIE-10 más frecuentes en urgencias"
    res = text_to_sql.execute_analytical_query(q)
    
    assert res["is_out_of_domain"] is False
    assert "c.cie10_code" in res["sql"]
    assert "c.descripcion" in res["sql"]
    assert "total_atenciones" in res["sql"]
    assert res["row_count"] > 0

def test_habeas_data_pii_deanonymization_blocked():
    """Strictly verify that questions asking for patient identification are blocked."""
    q = "Dame la cédula y nombre del paciente con apendicitis"
    res = text_to_sql.execute_analytical_query(q)
    
    assert res["is_out_of_domain"] is True
    assert res["is_pii_violation"] is True
    assert res["sql"] == ""
    assert "HABEAS DATA" in res["reason"]

    report = insight_generator.generate_report(res)
    assert report["chart_type"] == "out_of_domain"
    assert "Bloqueo por Habeas Data" in report["headline"]

def test_out_of_domain_queries_remain_blocked():
    """Verify non-healthcare and non-business entities are blocked."""
    q = "Cuál es la cotización de las acciones de Apple en Wall Street"
    res = text_to_sql.execute_analytical_query(q)
    
    assert res["is_out_of_domain"] is True
    assert res["sql"] == ""

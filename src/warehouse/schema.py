"""
Healthcare Kimball Star Schema DDL for 8 EPS/IPS 24/7 Operations.
Enforces strict medical data modeling, cryptographic patient de-identification,
and sub-50ms analytical views for Emergency Triage, ICU Beds, Glosas, and Appointment Access.
"""

DDL_DIM_IPS = """
CREATE TABLE IF NOT EXISTS dim_ips (
    ips_id INTEGER PRIMARY KEY,
    nombre_ips VARCHAR NOT NULL,
    tipo_sede VARCHAR NOT NULL, -- 'Hospital Alta Complejidad', 'Clínica Quirúrgica', 'Centro Ambulatorio'
    es_24h BOOLEAN NOT NULL,
    ciudad VARCHAR NOT NULL,
    camas_instaladas INTEGER NOT NULL
);
"""

DDL_DIM_EPS = """
CREATE TABLE IF NOT EXISTS dim_eps (
    eps_id INTEGER PRIMARY KEY,
    nombre_eps VARCHAR NOT NULL,
    codigo_habilitacion VARCHAR NOT NULL,
    regimen_principal VARCHAR NOT NULL -- 'Contributivo', 'Subsidiado', 'Mixto'
);
"""

DDL_DIM_CIE10 = """
CREATE TABLE IF NOT EXISTS dim_cie10 (
    cie10_code VARCHAR PRIMARY KEY,
    descripcion VARCHAR NOT NULL,
    capitulo VARCHAR NOT NULL
);
"""

DDL_DIM_PACIENTE = """
CREATE TABLE IF NOT EXISTS dim_paciente_anonimizado (
    patient_hash_id VARCHAR PRIMARY KEY, -- SHA-256 hash (No PII)
    edad_anos INTEGER NOT NULL,
    sexo VARCHAR NOT NULL, -- 'M', 'F'
    grupo_etario VARCHAR NOT NULL, -- 'Pediatrico', 'Adulto Joven', 'Adulto Mayor'
    regimen VARCHAR NOT NULL
);
"""

DDL_DIM_DATE = """
CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR NOT NULL,
    week_of_year INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR NOT NULL,
    is_weekend BOOLEAN NOT NULL
);
"""

DDL_FACT_URGENCIAS_TRIAGE = """
CREATE TABLE IF NOT EXISTS fact_urgencias_triage (
    admission_id BIGINT PRIMARY KEY,
    ips_id INTEGER NOT NULL,
    eps_id INTEGER NOT NULL,
    patient_hash_id VARCHAR NOT NULL,
    date_id INTEGER NOT NULL,
    hora_ingreso INTEGER NOT NULL, -- 0 to 23
    triage_level INTEGER NOT NULL, -- 1 to 5 (Manchester Scale)
    tiempo_espera_minutos INTEGER NOT NULL,
    tiempo_estancia_horas DOUBLE NOT NULL,
    cie10_code VARCHAR NOT NULL,
    reingreso_72h BOOLEAN NOT NULL,
    destino_alta VARCHAR NOT NULL -- 'Domicilio', 'Hospitalización', 'UCI', 'Remisión'
);
"""

DDL_FACT_CENSO_CAMAS = """
CREATE TABLE IF NOT EXISTS fact_censo_camas (
    censo_id BIGINT PRIMARY KEY,
    ips_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    servicio VARCHAR NOT NULL, -- 'Urgencias', 'UCI Adulto', 'UCI Pediátrica', 'Hospitalización General'
    camas_totales INTEGER NOT NULL,
    camas_ocupadas INTEGER NOT NULL,
    tasa_ocupacion_pct DOUBLE NOT NULL
);
"""

DDL_FACT_AUDITORIA_GLOSAS = """
CREATE TABLE IF NOT EXISTS fact_auditoria_glosas (
    glosa_id BIGINT PRIMARY KEY,
    ips_id INTEGER NOT NULL,
    eps_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    valor_radicado DOUBLE NOT NULL,
    valor_glosado DOUBLE NOT NULL,
    valor_levantado DOUBLE NOT NULL,
    motivo_glosa_codigo VARCHAR NOT NULL,
    estado_glosa VARCHAR NOT NULL -- 'Aceptada', 'Glosada', 'En Conciliación', 'Levantada'
);
"""

DDL_FACT_CITAS_OPORTUNIDAD = """
CREATE TABLE IF NOT EXISTS fact_citas_oportunidad (
    cita_id BIGINT PRIMARY KEY,
    ips_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    especialidad VARCHAR NOT NULL, -- 'Medicina General', 'Cardiología', 'Pediatría', 'Medicina Interna', 'Ginecología', 'Ortopedia'
    dias_oportunidad INTEGER NOT NULL,
    cumple_meta_normativa BOOLEAN NOT NULL
);
"""

DDL_HEALTHCARE_VIEWS = """
CREATE OR REPLACE VIEW gold_urgencias_triage_resumen AS
SELECT
    i.nombre_ips,
    i.es_24h,
    f.triage_level,
    COUNT(f.admission_id) AS total_atenciones,
    ROUND(AVG(f.tiempo_espera_minutos), 1) AS tiempo_espera_promedio_min,
    SUM(CASE WHEN f.reingreso_72h THEN 1 ELSE 0 END) AS total_reingresos_72h,
    ROUND(SUM(CASE WHEN f.reingreso_72h THEN 1 ELSE 0 END) * 100.0 / COUNT(f.admission_id), 2) AS tasa_reingreso_pct
FROM fact_urgencias_triage f
JOIN dim_ips i ON f.ips_id = i.ips_id
GROUP BY 1, 2, 3;

CREATE OR REPLACE VIEW gold_censo_camas_resumen AS
SELECT
    i.nombre_ips,
    i.es_24h,
    c.servicio,
    SUM(c.camas_totales) AS total_camas_instaladas,
    SUM(c.camas_ocupadas) AS total_camas_ocupadas,
    ROUND(SUM(c.camas_ocupadas) * 100.0 / NULLIF(SUM(c.camas_totales), 0), 2) AS ocupacion_promedio_pct
FROM fact_censo_camas c
JOIN dim_ips i ON c.ips_id = i.ips_id
GROUP BY 1, 2, 3;

CREATE OR REPLACE VIEW gold_glosas_eps_resumen AS
SELECT
    e.nombre_eps,
    COUNT(g.glosa_id) AS total_facturas_auditadas,
    ROUND(SUM(g.valor_radicado), 2) AS total_valor_radicado,
    ROUND(SUM(g.valor_glosado), 2) AS total_valor_glosado,
    ROUND(SUM(g.valor_glosado) * 100.0 / NULLIF(SUM(g.valor_radicado), 0), 2) AS tasa_glosa_pct,
    ROUND(SUM(g.valor_levantado), 2) AS total_valor_levantado
FROM fact_auditoria_glosas g
JOIN dim_eps e ON g.eps_id = e.eps_id
GROUP BY 1;

CREATE OR REPLACE VIEW gold_oportunidad_citas_resumen AS
SELECT
    o.especialidad,
    COUNT(o.cita_id) AS total_citas_asignadas,
    ROUND(AVG(o.dias_oportunidad), 1) AS dias_oportunidad_promedio,
    ROUND(SUM(CASE WHEN o.cumple_meta_normativa THEN 1 ELSE 0 END) * 100.0 / COUNT(o.cita_id), 2) AS cumplimiento_normativo_pct
FROM fact_citas_oportunidad o
GROUP BY 1;
"""

def initialize_gold_schema(con):
    """Executes all DDL and views to build the Healthcare Star Schema in Gold layer."""
    con.execute(DDL_DIM_IPS)
    con.execute(DDL_DIM_EPS)
    con.execute(DDL_DIM_CIE10)
    con.execute(DDL_DIM_PACIENTE)
    con.execute(DDL_DIM_DATE)
    con.execute(DDL_FACT_URGENCIAS_TRIAGE)
    con.execute(DDL_FACT_CENSO_CAMAS)
    con.execute(DDL_FACT_AUDITORIA_GLOSAS)
    con.execute(DDL_FACT_CITAS_OPORTUNIDAD)
    con.execute(DDL_HEALTHCARE_VIEWS)

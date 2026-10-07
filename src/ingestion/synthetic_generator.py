import hashlib
import random
from datetime import date, timedelta
import polars as pl
from src.config import settings

def generate_healthcare_dimensions() -> dict[str, pl.DataFrame]:
    """Generate official healthcare dimensions for the 8 EPS/IPS ecosystem."""
    
    # 1. dim_date (730 days: 2025 - 2026)
    start_date = date(2025, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(730)]
    dim_date = pl.DataFrame({
        "date_id": [int(d.strftime("%Y%m%d")) for d in dates],
        "full_date": dates,
        "year": [d.year for d in dates],
        "quarter": [(d.month - 1) // 3 + 1 for d in dates],
        "month": [d.month for d in dates],
        "month_name": [d.strftime("%B") for d in dates],
        "week_of_year": [d.isocalendar()[1] for d in dates],
        "day_of_month": [d.day for d in dates],
        "day_of_week": [d.isoweekday() for d in dates],
        "day_name": [d.strftime("%A") for d in dates],
        "is_weekend": [d.isoweekday() in (6, 7) for d in dates],
    })

    # 2. dim_ips (The 8 hospital and clinical branches, 4 of which are 24/7)
    ips_data = [
        (1, "Hospital Universitario Central", "Hospital Alta Complejidad", True, "Bogotá", 320),
        (2, "Clínica Pediátrica Santa María", "Clínica Quirúrgica / Pediatría", True, "Medellín", 180),
        (3, "Hospital Traumatológico del Norte", "Hospital Traumatología & Urgencias", True, "Cali", 240),
        (4, "Clínica Metropolitana Sur", "Hospital Materno-Infantil", True, "Barranquilla", 210),
        (5, "Centro Médico Ambulatorio Chapinero", "Centro Ambulatorio & Diagnóstico", False, "Bogotá", 0),
        (6, "IPS Especializada Poblado", "Centro de Especialistas", False, "Medellín", 0),
        (7, "Unidad de Atención Básica Teusaquillo", "Centro Médico Consulta Externa", False, "Bogotá", 0),
        (8, "Policlínica Ambulatoria Occidente", "Centro de Citas & Rehabilitación", False, "Cali", 0),
    ]
    dim_ips = pl.DataFrame({
        "ips_id": [x[0] for x in ips_data],
        "nombre_ips": [x[1] for x in ips_data],
        "tipo_sede": [x[2] for x in ips_data],
        "es_24h": [x[3] for x in ips_data],
        "ciudad": [x[4] for x in ips_data],
        "camas_instaladas": [x[5] for x in ips_data],
    })

    # 3. dim_eps (The major healthcare insurance providers)
    eps_data = [
        (1, "Sura EPS", "EPS001", "Contributivo"),
        (2, "Sanitas EPS", "EPS002", "Contributivo"),
        (3, "Nueva EPS", "EPS003", "Mixto"),
        (4, "Salud Total", "EPS004", "Contributivo"),
        (5, "Compensar EPS", "EPS005", "Contributivo"),
        (6, "Coosalud EPS", "EPS006", "Subsidiado"),
        (7, "Famisanar EPS", "EPS007", "Contributivo"),
        (8, "Mutual Ser", "EPS008", "Subsidiado"),
    ]
    dim_eps = pl.DataFrame({
        "eps_id": [x[0] for x in eps_data],
        "nombre_eps": [x[1] for x in eps_data],
        "codigo_habilitacion": [x[2] for x in eps_data],
        "regimen_principal": [x[3] for x in eps_data],
    })

    # 4. dim_cie10 (Top clinical diagnoses)
    cie10_data = [
        ("I10", "Hipertensión esencial (primaria)", "Enfermedades del sistema circulatorio"),
        ("J069", "Infección aguda respiratoria de las vías superiores", "Enfermedades del sistema respiratorio"),
        ("E119", "Diabetes mellitus tipo 2 no especificada", "Enfermedades endocrinas y metabólicas"),
        ("J189", "Neumonía no especificada", "Enfermedades del sistema respiratorio"),
        ("K358", "Apendicitis aguda", "Enfermedades del sistema digestivo"),
        ("S299", "Traumatismo del tórax no especificado", "Traumatismos y envenenamientos"),
        ("N390", "Infección de vías urinarias", "Enfermedades del sistema genitourinario"),
        ("R104", "Dolor abdominal no especificado", "Síntomas y signos clínicos"),
        ("K297", "Gastritis no especificada", "Enfermedades del sistema digestivo"),
        ("A090", "Gastroenteritis y colitis de origen infeccioso", "Enfermedades infecciosas"),
    ]
    dim_cie10 = pl.DataFrame({
        "cie10_code": [x[0] for x in cie10_data],
        "descripcion": [x[1] for x in cie10_data],
        "capitulo": [x[2] for x in cie10_data],
    })

    # 5. dim_paciente_anonimizado (10,000 anonymized patient profiles with SHA-256 tokens)
    p_ids = []
    edades = []
    sexos = []
    grupos = []
    regimenes = []
    for i in range(1, 10001):
        # Cryptographic irreversible hash of simulated citizen ID for Habeas Data compliance
        h = hashlib.sha256(f"COL-PATIENT-{i:07d}-SECURE".encode()).hexdigest()[:16]
        p_ids.append(f"PAC-{h}")
        age = random.randint(1, 89)
        edades.append(age)
        sexos.append("F" if random.random() > 0.48 else "M")
        if age < 18:
            grupos.append("Pediátrico")
        elif age < 60:
            grupos.append("Adulto")
        else:
            grupos.append("Adulto Mayor")
        regimenes.append("Contributivo" if i % 3 != 0 else "Subsidiado")

    dim_paciente = pl.DataFrame({
        "patient_hash_id": p_ids,
        "edad_anos": edades,
        "sexo": sexos,
        "grupo_etario": grupos,
        "regimen": regimenes,
    })

    return {
        "dim_date": dim_date,
        "dim_ips": dim_ips,
        "dim_eps": dim_eps,
        "dim_cie10": dim_cie10,
        "dim_paciente_anonimizado": dim_paciente,
    }


def generate_massive_hospital_events(
    n_urgencias: int = 400_000,
    dims: dict[str, pl.DataFrame] = None
) -> dict[str, pl.DataFrame]:
    """
    Generate atomic hospital fact datasets for the 8 EPS/IPS 24/7 ecosystem.
    Vectorized with Polars for sub-second performance.
    """
    if dims is None:
        dims = generate_healthcare_dimensions()

    date_ids = dims["dim_date"]["date_id"].to_list()
    # 24/7 IPS IDs are 1, 2, 3, 4
    ips_24h_ids = [1, 2, 3, 4]
    all_ips_ids = [1, 2, 3, 4, 5, 6, 7, 8]
    eps_ids = dims["dim_eps"]["eps_id"].to_list()
    cie10_codes = dims["dim_cie10"]["cie10_code"].to_list()
    patient_hashes = dims["dim_paciente_anonimizado"]["patient_hash_id"].to_list()

    # 1. FACT_URGENCIAS_TRIAGE (Only 24/7 IPS branches attend Emergency Triage)
    triage_levels = [1, 2, 3, 4, 5]
    triage_weights = [0.03, 0.15, 0.50, 0.22, 0.10] # Manchester distribution
    destinos = ["Domicilio", "Hospitalización", "UCI", "Remisión"]

    chosen_triage = random.choices(triage_levels, weights=triage_weights, k=n_urgencias)
    wait_times = []
    stay_times = []
    for t in chosen_triage:
        if t == 1:
            wait_times.append(0) # Inmediato
            stay_times.append(round(random.uniform(6.0, 48.0), 1))
        elif t == 2:
            wait_times.append(random.randint(5, 45)) # Meta: < 30 min
            stay_times.append(round(random.uniform(4.0, 24.0), 1))
        elif t == 3:
            wait_times.append(random.randint(25, 120))
            stay_times.append(round(random.uniform(2.0, 12.0), 1))
        elif t == 4:
            wait_times.append(random.randint(45, 180))
            stay_times.append(round(random.uniform(1.0, 4.0), 1))
        else: # Triage 5
            wait_times.append(random.randint(60, 240))
            stay_times.append(round(random.uniform(0.5, 2.0), 1))

    fact_urgencias = pl.DataFrame({
        "admission_id": pl.int_range(1, n_urgencias + 1, dtype=pl.Int64, eager=True),
        "ips_id": [random.choice(ips_24h_ids) for _ in range(n_urgencias)],
        "eps_id": [random.choice(eps_ids) for _ in range(n_urgencias)],
        "patient_hash_id": [random.choice(patient_hashes) for _ in range(n_urgencias)],
        "date_id": [random.choice(date_ids) for _ in range(n_urgencias)],
        "hora_ingreso": [random.randint(0, 23) for _ in range(n_urgencias)],
        "triage_level": chosen_triage,
        "tiempo_espera_minutos": wait_times,
        "tiempo_estancia_horas": stay_times,
        "cie10_code": [random.choice(cie10_codes) for _ in range(n_urgencias)],
        "reingreso_72h": [random.random() < 0.045 for _ in range(n_urgencias)],
        "destino_alta": [random.choice(destinos) for _ in range(n_urgencias)],
    })

    # 2. FACT_CENSO_CAMAS (Daily bed occupancy for 24h branches)
    censo_records = []
    c_id = 1
    servicios = [
        ("Urgencias", 60),
        ("Hospitalización General", 120),
        ("UCI Adulto", 30),
        ("UCI Pediátrica", 15)
    ]
    # Sample 365 days across 4 24h IPS
    sample_dates = date_ids[:365]
    for d_id in sample_dates:
        for ips_id in ips_24h_ids:
            for s_nom, base_beds in servicios:
                ocupadas = min(base_beds, int(base_beds * random.uniform(0.70, 0.98)))
                pct = round((ocupadas / base_beds) * 100, 2)
                censo_records.append({
                    "censo_id": c_id,
                    "ips_id": ips_id,
                    "date_id": d_id,
                    "servicio": s_nom,
                    "camas_totales": base_beds,
                    "camas_ocupadas": ocupadas,
                    "tasa_ocupacion_pct": pct,
                })
                c_id += 1
    fact_censo_camas = pl.DataFrame(censo_records)

    # 3. FACT_AUDITORIA_GLOSAS (Audit records of medical bills & documents)
    n_glosas = 100_000
    radicado_vals = [round(random.uniform(250_000.0, 15_000_000.0), 2) for _ in range(n_glosas)]
    glosado_vals = []
    levantado_vals = []
    estados = []
    motivos = ["GL-01 Pertinencia Médica", "GL-02 Soporte Incompleto", "GL-03 Tarifa no pactada", "GL-04 Autorización extemporánea"]
    for r in radicado_vals:
        tiene_glosa = random.random() < 0.22 # 22% glosa promedio
        if tiene_glosa:
            g_pct = random.uniform(0.05, 0.40)
            g_val = round(r * g_pct, 2)
            glosado_vals.append(g_val)
            l_val = round(g_val * random.uniform(0.40, 0.90), 2)
            levantado_vals.append(l_val)
            estados.append(random.choice(["Glosada", "En Conciliación", "Levantada"]))
        else:
            glosado_vals.append(0.0)
            levantado_vals.append(0.0)
            estados.append("Aceptada")

    fact_glosas = pl.DataFrame({
        "glosa_id": pl.int_range(1, n_glosas + 1, dtype=pl.Int64, eager=True),
        "ips_id": [random.choice(all_ips_ids) for _ in range(n_glosas)],
        "eps_id": [random.choice(eps_ids) for _ in range(n_glosas)],
        "date_id": [random.choice(date_ids) for _ in range(n_glosas)],
        "valor_radicado": radicado_vals,
        "valor_glosado": glosado_vals,
        "valor_levantado": levantado_vals,
        "motivo_glosa_codigo": [random.choice(motivos) for _ in range(n_glosas)],
        "estado_glosa": estados,
    })

    # 4. FACT_CITAS_OPORTUNIDAD (Outpatient appointment appointment wait times)
    n_citas = 150_000
    especialidades = ["Medicina General", "Cardiología", "Pediatría", "Medicina Interna", "Ginecología", "Ortopedia"]
    dias = []
    cumple = []
    for _ in range(n_citas):
        esp = random.choice(especialidades)
        if esp == "Medicina General":
            d = random.randint(1, 6)
            dias.append(d)
            cumple.append(d <= 3) # Meta normativa: <= 3 días
        else:
            d = random.randint(5, 30)
            dias.append(d)
            cumple.append(d <= 15) # Meta especializada: <= 15 días

    fact_citas = pl.DataFrame({
        "cita_id": pl.int_range(1, n_citas + 1, dtype=pl.Int64, eager=True),
        "ips_id": [random.choice(all_ips_ids) for _ in range(n_citas)],
        "date_id": [random.choice(date_ids) for _ in range(n_citas)],
        "especialidad": [random.choice(especialidades) for _ in range(n_citas)],
        "dias_oportunidad": dias,
        "cumple_meta_normativa": cumple,
    })

    return {
        "fact_urgencias_triage": fact_urgencias,
        "fact_censo_camas": fact_censo_camas,
        "fact_auditoria_glosas": fact_glosas,
        "fact_citas_oportunidad": fact_citas,
    }

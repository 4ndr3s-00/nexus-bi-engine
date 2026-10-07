from pydantic import BaseModel, Field
from typing import Optional, Any, List

class SeedRequest(BaseModel):
    n_rows: int = Field(default=500_000, ge=10_000, le=5_000_000, description="Cantidad de registros a ingestar")

class NaturalQueryRequest(BaseModel):
    question: str = Field(..., min_length=2, description="Pregunta en lenguaje natural para la data")
    custom_sql: Optional[str] = Field(default=None, description="SQL opcional si se desea ejecutar una consulta manual")

class KPICard(BaseModel):
    label: str
    value: str
    change: str
    trend: str = "up"

class ExecutiveReportResponse(BaseModel):
    question: str
    sql: str
    latency_ms: float
    headline: str
    summary: str
    chart_type: str = "general_bars"
    kpi_cards: list[KPICard]
    highlights: list[str]
    recommendations: list[str]
    table_data: list[dict[str, Any]]
    dimensions: list[str]
    direct_answer: Optional[str] = None
    is_out_of_domain: bool = False

class DashboardOverviewResponse(BaseModel):
    kpis: list[KPICard]
    monthly_trend: list[dict[str, Any]]
    category_breakdown: list[dict[str, Any]]
    regional_breakdown: list[dict[str, Any]]
    lakehouse_stats: dict[str, Any]
    query_latency_ms: float

# -------------------------------------------------------------
# Hospital & Strata Core Models
# -------------------------------------------------------------
class HospitalOverviewResponse(BaseModel):
    kpis: list[KPICard]
    triage_by_level: list[dict[str, Any]]
    bed_occupancy_by_ips: list[dict[str, Any]]
    glosas_by_eps: list[dict[str, Any]]
    appointment_opportunity: list[dict[str, Any]]
    network_summary: dict[str, Any]
    query_latency_ms: float

class DocumentEvaluateRequest(BaseModel):
    document_id: str
    document_type: str
    raw_text: Optional[str] = None
    file_path: Optional[str] = None
    ips_name: Optional[str] = "Hospital Universitario Central"
    eps_name: Optional[str] = "Sura EPS"

class AuditorDecisionRequest(BaseModel):
    document_id: str
    decision: str = Field(..., description="'Aprobado', 'Glosado' o 'Subsanación'")
    auditor_id: str = "AUD-101"
    auditor_name: str = "Auditor EPS"
    motivo_glosa: Optional[str] = None
    observaciones: Optional[str] = None

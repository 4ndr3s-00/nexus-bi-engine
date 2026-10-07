from typing import Dict, Optional
import polars as pl
from src.ingestion.gateway import HospitalDataSource
from src.ingestion.synthetic_generator import (
    generate_healthcare_dimensions,
    generate_massive_hospital_events
)

class MockHospitalAdapter(HospitalDataSource):
    """
    Simulated data adapter for local development and smoke tests.
    Generates realistic 24/7 hospital network events across 8 EPS/IPS.
    """
    def __init__(self):
        self._cached_dims: Optional[Dict[str, pl.DataFrame]] = None

    def fetch_dimensions(self) -> Dict[str, pl.DataFrame]:
        if self._cached_dims is None:
            self._cached_dims = generate_healthcare_dimensions()
        return self._cached_dims

    def fetch_admissions(self, n_rows: int = 400_000, dims: Optional[Dict[str, pl.DataFrame]] = None) -> pl.DataFrame:
        target_dims = dims or self.fetch_dimensions()
        events = generate_massive_hospital_events(n_urgencias=n_rows, dims=target_dims)
        return events["fact_urgencias_triage"]

    def fetch_beds(self, dims: Optional[Dict[str, pl.DataFrame]] = None) -> pl.DataFrame:
        target_dims = dims or self.fetch_dimensions()
        events = generate_massive_hospital_events(n_urgencias=1000, dims=target_dims)
        return events["fact_censo_camas"]

    def fetch_glosas(self, dims: Optional[Dict[str, pl.DataFrame]] = None) -> pl.DataFrame:
        target_dims = dims or self.fetch_dimensions()
        events = generate_massive_hospital_events(n_urgencias=1000, dims=target_dims)
        return events["fact_auditoria_glosas"]

    def fetch_appointments(self, dims: Optional[Dict[str, pl.DataFrame]] = None) -> pl.DataFrame:
        target_dims = dims or self.fetch_dimensions()
        events = generate_massive_hospital_events(n_urgencias=1000, dims=target_dims)
        return events["fact_citas_oportunidad"]

import httpx
from typing import Dict, Optional, Any
import polars as pl
from rich.console import Console
from src.config import settings
from src.ingestion.gateway import HospitalDataSource
from src.ingestion.adapters.mock_adapter import MockHospitalAdapter

console = Console()

class RestHospitalAdapter(HospitalDataSource):
    """
    Connects to external healthcare EHR/HIS REST APIs (e.g. SAP, Cerner, local Colombian HIS).
    Pulls live clinical admission, bed census, and glosa records into Polars DataFrames.
    If external API is unreachable or offline, safely logs and falls back to Mock adapter.
    """
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_sec: float = 3.0
    ):
        self.base_url = (base_url or settings.EHR_API_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.EHR_API_KEY
        self.timeout_sec = timeout_sec
        self._fallback_adapter = MockHospitalAdapter()

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "Nexus-BI-Engine/1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def fetch_dimensions(self) -> Dict[str, pl.DataFrame]:
        try:
            with httpx.Client(timeout=self.timeout_sec) as client:
                res = client.get(f"{self.base_url}/dimensions", headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    return {
                        "dim_ips": pl.DataFrame(data.get("dim_ips", [])),
                        "dim_eps": pl.DataFrame(data.get("dim_eps", [])),
                        "dim_cie10": pl.DataFrame(data.get("dim_cie10", [])),
                        "dim_date": pl.DataFrame(data.get("dim_date", []))
                    }
        except Exception as e:
            console.print(f"[yellow][!] External EHR dimensions pull failed ({e}). Using resilient fallback.[/yellow]")
        return self._fallback_adapter.fetch_dimensions()

    def fetch_admissions(self, n_rows: int = 400_000, dims: Optional[Dict[str, pl.DataFrame]] = None) -> pl.DataFrame:
        try:
            with httpx.Client(timeout=self.timeout_sec) as client:
                res = client.get(f"{self.base_url}/admissions?limit={n_rows}", headers=self._get_headers())
                if res.status_code == 200:
                    rows = res.json().get("admissions", [])
                    if rows:
                        return pl.DataFrame(rows)
        except Exception as e:
            console.print(f"[yellow][!] External EHR admissions pull failed ({e}). Using resilient fallback.[/yellow]")
        return self._fallback_adapter.fetch_admissions(n_rows=n_rows, dims=dims)

    def fetch_beds(self, dims: Optional[Dict[str, pl.DataFrame]] = None) -> pl.DataFrame:
        try:
            with httpx.Client(timeout=self.timeout_sec) as client:
                res = client.get(f"{self.base_url}/beds", headers=self._get_headers())
                if res.status_code == 200:
                    rows = res.json().get("beds", [])
                    if rows:
                        return pl.DataFrame(rows)
        except Exception as e:
            console.print(f"[yellow][!] External EHR bed census pull failed ({e}). Using resilient fallback.[/yellow]")
        return self._fallback_adapter.fetch_beds(dims=dims)

    def fetch_glosas(self, dims: Optional[Dict[str, pl.DataFrame]] = None) -> pl.DataFrame:
        try:
            with httpx.Client(timeout=self.timeout_sec) as client:
                res = client.get(f"{self.base_url}/glosas", headers=self._get_headers())
                if res.status_code == 200:
                    rows = res.json().get("glosas", [])
                    if rows:
                        return pl.DataFrame(rows)
        except Exception as e:
            console.print(f"[yellow][!] External EHR glosas pull failed ({e}). Using resilient fallback.[/yellow]")
        return self._fallback_adapter.fetch_glosas(dims=dims)

    def fetch_appointments(self, dims: Optional[Dict[str, pl.DataFrame]] = None) -> pl.DataFrame:
        try:
            with httpx.Client(timeout=self.timeout_sec) as client:
                res = client.get(f"{self.base_url}/appointments", headers=self._get_headers())
                if res.status_code == 200:
                    rows = res.json().get("appointments", [])
                    if rows:
                        return pl.DataFrame(rows)
        except Exception as e:
            console.print(f"[yellow][!] External EHR appointments pull failed ({e}). Using resilient fallback.[/yellow]")
        return self._fallback_adapter.fetch_appointments(dims=dims)

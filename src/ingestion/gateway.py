import abc
from typing import Dict, Any, Optional
import polars as pl
from rich.console import Console
from src.config import settings

console = Console()

class HospitalDataSource(abc.ABC):
    """
    Abstract interface for hospital data sources.
    Decouples the Medallion Pipeline from specific storage or origin systems
    (whether simulated in development or pulling from external EHR/HIS REST APIs).
    """
    @abc.abstractmethod
    def fetch_dimensions(self) -> Dict[str, pl.DataFrame]:
        """Fetch dimensional catalog (dim_ips, dim_eps, dim_cie10, dim_date)."""
        pass

    @abc.abstractmethod
    def fetch_admissions(self, n_rows: int = 400_000, dims: Optional[Dict[str, pl.DataFrame]] = None) -> pl.DataFrame:
        """Fetch emergency room admissions with Triage Manchester."""
        pass

    @abc.abstractmethod
    def fetch_beds(self, dims: Optional[Dict[str, pl.DataFrame]] = None) -> pl.DataFrame:
        """Fetch daily ICU and inpatient bed census."""
        pass

    @abc.abstractmethod
    def fetch_glosas(self, dims: Optional[Dict[str, pl.DataFrame]] = None) -> pl.DataFrame:
        """Fetch RIPS audit billing records with glosas."""
        pass

    @abc.abstractmethod
    def fetch_appointments(self, dims: Optional[Dict[str, pl.DataFrame]] = None) -> pl.DataFrame:
        """Fetch outpatient appointment scheduling and lead-times."""
        pass


class IngestionGateway:
    """
    Central gateway for hospital data ingestion into the Lakehouse.
    Routes queries to the appropriate adapter based on settings.DATA_SOURCE_PROVIDER.
    Supports seamless switching between Mock/Development, REST API Pull, and Webhook Push.
    """
    def __init__(self):
        self._adapters: Dict[str, HospitalDataSource] = {}
        self._init_default_adapters()

    def _init_default_adapters(self):
        # Lazy import to avoid circular dependencies
        from src.ingestion.adapters.mock_adapter import MockHospitalAdapter
        from src.ingestion.adapters.rest_adapter import RestHospitalAdapter
        
        self.register_adapter("mock", MockHospitalAdapter())
        self.register_adapter("rest", RestHospitalAdapter())

    def register_adapter(self, name: str, adapter: HospitalDataSource):
        self._adapters[name.lower()] = adapter

    def get_adapter(self, provider: Optional[str] = None) -> HospitalDataSource:
        name = (provider or settings.DATA_SOURCE_PROVIDER).lower()
        if name not in self._adapters:
            console.print(f"[yellow][!] Provider '{name}' not found. Falling back to 'mock'.[/yellow]")
            return self._adapters.get("mock")
        return self._adapters[name]

    def load_all_events(self, n_urgencias: int = 400_000, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Loads all dimensions and facts from the active data source adapter.
        """
        adapter = self.get_adapter(provider)
        dims = adapter.fetch_dimensions()
        
        admissions = adapter.fetch_admissions(n_rows=n_urgencias, dims=dims)
        beds = adapter.fetch_beds(dims=dims)
        glosas = adapter.fetch_glosas(dims=dims)
        appointments = adapter.fetch_appointments(dims=dims)

        return {
            "dimensions": dims,
            "facts": {
                "fact_urgencias_triage": admissions,
                "fact_censo_camas": beds,
                "fact_auditoria_glosas": glosas,
                "fact_citas_oportunidad": appointments
            }
        }

ingestion_gateway = IngestionGateway()

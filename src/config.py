from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nexus BI Engine"
    API_V1_STR: str = "/api/v1"
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    BRONZE_DIR: Path = DATA_DIR / "bronze"
    SILVER_DIR: Path = DATA_DIR / "silver"
    GOLD_DIR: Path = DATA_DIR / "gold"
    
    # Database
    DUCKDB_PATH: Path = GOLD_DIR / "lakehouse.duckdb"
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8080
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Ensure directories exist
settings.BRONZE_DIR.mkdir(parents=True, exist_ok=True)
settings.SILVER_DIR.mkdir(parents=True, exist_ok=True)
settings.GOLD_DIR.mkdir(parents=True, exist_ok=True)

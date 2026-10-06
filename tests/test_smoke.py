import pytest
from fastapi.testclient import TestClient
from src.api.server import app
from src.config import settings

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Nexus BI Engine"

def test_lakehouse_directories():
    assert settings.BRONZE_DIR.exists()
    assert settings.SILVER_DIR.exists()
    assert settings.GOLD_DIR.exists()

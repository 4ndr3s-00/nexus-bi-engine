from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="High-performance Lakehouse & AI-Powered Business Intelligence Platform",
    version="0.1.0",
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "0.1.0",
        "lakehouse": {
            "bronze": str(settings.BRONZE_DIR),
            "silver": str(settings.SILVER_DIR),
            "gold": str(settings.GOLD_DIR),
        }
    }

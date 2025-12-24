"""
ML Predictor Service - Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog
import uvicorn

from .config import settings
from .api import predict, health

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="MedBot ML Predictor",
    description="XGBoost-based predictive modeling for patient risk stratification",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(predict.router, prefix="/api", tags=["Predictions"])


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info(
        "Starting ML Predictor service",
        service=settings.SERVICE_NAME,
        port=settings.PORT
    )
    
    # Load models on startup
    try:
        from .ml.model_inference import ModelPredictor
        # Warm up models
        ModelPredictor.load_models()
        logger.info("Models loaded successfully")
    except Exception as e:
        logger.error("Failed to load models", error=str(e))
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down ML Predictor service")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )

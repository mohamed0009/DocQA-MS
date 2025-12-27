"""
ML Predictor Service - Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog
import uvicorn
import sys
import os

from .config import settings
from .api import predict, health

# Add shared module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../shared'))

try:
    from eureka_client import EurekaServiceRegistry
    EUREKA_AVAILABLE = True
except ImportError:
    EUREKA_AVAILABLE = False
    structlog.get_logger().warning("Eureka client not available")

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
    
    # Register with Eureka
    global eureka_registry
    eureka_registry = None
    if EUREKA_AVAILABLE and settings.ENABLE_EUREKA:
        try:
            eureka_registry = EurekaServiceRegistry(
                service_name="ML-PREDICTOR",
                service_port=8000,
                eureka_server_url=settings.EUREKA_SERVER_URL,
                instance_host=settings.INSTANCE_HOST
            )
            eureka_registry.register()
            logger.info("✓ ML Predictor registered with Eureka")
        except Exception as e:
            logger.error(f"Failed to register with Eureka: {e}")
    
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
    
    # Deregister from Eureka
    global eureka_registry
    if eureka_registry:
        try:
            eureka_registry.deregister()
            logger.info("✓ ML Predictor deregistered from Eureka")
        except Exception as e:
            logger.error(f"Error deregistering from Eureka: {e}")
            
    logger.info("Shutting down ML Predictor service")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )

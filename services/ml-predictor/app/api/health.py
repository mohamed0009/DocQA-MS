"""
Health check API endpoint
"""

from fastapi import APIRouter
import structlog

from ..schemas.prediction import HealthResponse
from ..config import settings

logger = structlog.get_logger()
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns service status and loaded models information
    """
    try:
        from ..ml.model_inference import ModelPredictor
        
        models_loaded = ModelPredictor.are_models_loaded()
        available_models = ModelPredictor.get_available_models()
        
        return HealthResponse(
            status="healthy" if models_loaded else "degraded",
            service=settings.SERVICE_NAME,
            version="1.0.0",
            models_loaded=models_loaded,
            available_models=available_models
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return HealthResponse(
            status="unhealthy",
            service=settings.SERVICE_NAME,
            version="1.0.0",
            models_loaded=False,
            available_models=[]
        )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes
    
    Returns 200 if service is ready to accept requests
    """
    from ..ml.model_inference import ModelPredictor
    
    if ModelPredictor.are_models_loaded():
        return {"status": "ready"}
    else:
        return {"status": "not ready"}, 503


@router.get("/live")
async def liveness_check():
    """
    Liveness check for Kubernetes
    
    Returns 200 if service is alive
    """
    return {"status": "alive"}

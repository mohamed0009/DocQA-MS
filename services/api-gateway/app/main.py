from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import logging
import sys
import os
from .config import get_settings
from .routes import documents, qa, search, comparative, audit, health, synthesis

# Add shared module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../shared'))

try:
    from eureka_client import EurekaServiceRegistry
    EUREKA_AVAILABLE = True
except ImportError:
    EUREKA_AVAILABLE = False
    logging.warning("Eureka client not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API Gateway for MedBot Intelligence Platform"
)

# Eureka client instance
eureka_registry = None


@app.on_event("startup")
async def startup_event():
    """Register with Eureka on startup"""
    global eureka_registry
    if EUREKA_AVAILABLE and settings.enable_eureka:
        try:
            eureka_registry = EurekaServiceRegistry(
                service_name=settings.service_name,
                service_port=8000,
                eureka_server_url=settings.eureka_server_url,
                instance_host=settings.instance_host
            )
            eureka_registry.register()
            logger.info("✓ API Gateway registered with Eureka")
        except Exception as e:
            logger.error(f"Failed to register with Eureka: {e}")
    else:
        logger.info("Eureka registration disabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Deregister from Eureka on shutdown"""
    global eureka_registry
    if eureka_registry:
        try:
            eureka_registry.deregister()
            logger.info("✓ API Gateway deregistered from Eureka")
        except Exception as e:
            logger.error(f"Error deregistering from Eureka: {e}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(qa.router, prefix="/api/v1/qa", tags=["Q&A"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(synthesis.router, prefix="/api/v1/synthesis", tags=["Synthesis"])
app.include_router(comparative.router, prefix="/api/v1/comparative", tags=["Comparative Analysis"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.exception_handler(httpx.HTTPError)
async def http_exception_handler(request: Request, exc: httpx.HTTPError):
    """Handle HTTP errors from downstream services"""
    logger.error(f"HTTP error occurred: {exc}")
    return JSONResponse(
        status_code=503,
        content={"detail": "Service temporarily unavailable"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

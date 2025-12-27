"""SyntheseComparative - Main Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
import sys
import os

from .database import engine, Base
from .api import synthesis
from .config import settings

# Add shared module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../shared'))

try:
    from eureka_client import EurekaServiceRegistry
    EUREKA_AVAILABLE = True
except ImportError:
    EUREKA_AVAILABLE = False
    structlog.get_logger().warning("Eureka client not available")

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SyntheseComparative service...")
    Base.metadata.create_all(bind=engine)
    
    # Register with Eureka
    eureka_registry = None
    if EUREKA_AVAILABLE and settings.ENABLE_EUREKA:
        try:
            eureka_registry = EurekaServiceRegistry(
                service_name="SYNTHESE-COMPARATIVE",
                service_port=8000,
                eureka_server_url=settings.EUREKA_SERVER_URL,
                instance_host=settings.INSTANCE_HOST
            )
            eureka_registry.register()
            logger.info("✓ SyntheseComparative registered with Eureka")
        except Exception as e:
            logger.error(f"Failed to register with Eureka: {e}")
            
    logger.info("SyntheseComparative started")
    yield
    
    # Deregister from Eureka
    if eureka_registry:
        try:
            eureka_registry.deregister()
            logger.info("✓ SyntheseComparative deregistered from Eureka")
        except Exception as e:
            logger.error(f"Error deregistering from Eureka: {e}")
            
    logger.info("Shutting down SyntheseComparative...")

app = FastAPI(
    title="MedBot Intelligence: SyntheseComparative",
    description="Patient Summary and Comparative Analysis Service",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(synthesis.router, prefix="/api/v1/synthesis", tags=["synthesis"])

@app.get("/")
async def root():
    return {"service": "SyntheseComparative", "version": "1.0.0", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "synthese-comparative"}

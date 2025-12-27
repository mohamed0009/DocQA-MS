"""
IndexeurSémantique Service - Main Application
Semantic Indexing and Search Service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
import sys
import os

from .database import engine, Base
from .api import search
from .config import settings

# Add shared module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../shared'))

try:
    from eureka_client import EurekaServiceRegistry
    EUREKA_AVAILABLE = True
except ImportError:
    EUREKA_AVAILABLE = False
    structlog.get_logger().warning("Eureka client not available")

# Configure logging
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting IndexeurSémantique service...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Register with Eureka
    eureka_registry = None
    if EUREKA_AVAILABLE and settings.ENABLE_EUREKA:
        try:
            eureka_registry = EurekaServiceRegistry(
                service_name="INDEXEUR-SEMANTIQUE",
                service_port=8000,
                eureka_server_url=settings.EUREKA_SERVER_URL,
                instance_host=settings.INSTANCE_HOST
            )
            eureka_registry.register()
            logger.info("✓ IndexeurSémantique registered with Eureka")
        except Exception as e:
            logger.error(f"Failed to register with Eureka: {e}")
    
    logger.info("IndexeurSémantique service started successfully")
    yield
    
    # Deregister from Eureka
    if eureka_registry:
        try:
            eureka_registry.deregister()
            logger.info("✓ IndexeurSémantique deregistered from Eureka")
        except Exception as e:
            logger.error(f"Error deregistering from Eureka: {e}")
    
    logger.info("Shutting down IndexeurSémantique service...")


# Create FastAPI application
app = FastAPI(
    title="MedBot Intelligence: IndexeurSémantique Service",
    description="Semantic Document Indexing and Search Service using FAISS",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    search.router,
    prefix="/api/v1/search",
    tags=["search"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "IndexeurSémantique",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "indexeur-semantique"
    }

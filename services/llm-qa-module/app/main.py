"""
LLM QA Module - Main Application
AI-Powered Question Answering with RAG
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
import sys
import os

from .database import engine, Base
from .api import qa
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
    logger.info("Starting LLM QA Module...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize LLM (warm up) - Optional for standalone mode
    try:
        from .llm import get_llm
        get_llm()
        logger.info("LLM initialized successfully")
    except ImportError:
        logger.warning("LLM module not found - running in standalone mode without LLM")
    except Exception as e:
        logger.warning("LLM initialization skipped", error=str(e))
    
    # Register with Eureka
    eureka_registry = None
    if EUREKA_AVAILABLE and settings.ENABLE_EUREKA:
        try:
            eureka_registry = EurekaServiceRegistry(
                service_name="LLM-QA-MODULE",
                service_port=8000,
                eureka_server_url=settings.EUREKA_SERVER_URL,
                instance_host=settings.INSTANCE_HOST
            )
            eureka_registry.register()
            logger.info("✓ LLM QA Module registered with Eureka")
        except Exception as e:
            logger.error(f"Failed to register with Eureka: {e}")
            
    logger.info("LLM QA Module started successfully")
    yield
    
    # Deregister from Eureka
    if eureka_registry:
        try:
            eureka_registry.deregister()
            logger.info("✓ LLM QA Module deregistered from Eureka")
        except Exception as e:
            logger.error(f"Error deregistering from Eureka: {e}")
            
    logger.info("Shutting down LLM QA Module...")


# Create FastAPI application
app = FastAPI(
    title="MedBot Intelligence: LLM QA Module",
    description="AI-Powered Medical Question Answering with RAG and Citations",
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
    qa.router,
    prefix="/api/v1/qa",
    tags=["qa"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "LLM QA Module",
        "version": "1.0.0",
        "status": "healthy",
        "llm_provider": settings.LLM_PROVIDER,
        "model": settings.OPENAI_MODEL if settings.LLM_PROVIDER == "openai" else settings.LOCAL_MODEL_NAME
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "llm-qa-module"
    }

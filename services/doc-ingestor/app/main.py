"""
DocIngestor Service - Main Application
Medical Document Ingestion and Parsing Service
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
from typing import List
import os

from .database import engine, Base, get_db
from .api import documents
from .config import settings

# Configure logging
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting DocIngestor service...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Create necessary directories
    os.makedirs(settings.DOCUMENT_STORAGE_PATH, exist_ok=True)
    
    logger.info("DocIngestor service started successfully")
    yield
    logger.info("Shutting down DocIngestor service...")


# Create FastAPI application
app = FastAPI(
    title="MedBot Intelligence: DocIngestor Service",
    description="Medical Document Ingestion and Parsing Service",
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
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "DocIngestor",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "doc-ingestor"
    }

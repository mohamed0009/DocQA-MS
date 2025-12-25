"""
Configuration management for DocIngestor service
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Service
    SERVICE_NAME: str = "doc-ingestor"
    LOG_LEVEL: str = "INFO"
    
    # Database - Using SQLite for local development
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./doc_ingestor.db")
    
    # RabbitMQ (optional for local dev)
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"
    RABBITMQ_QUEUE: str = "document_processing"
    
    # File Storage - Windows compatible path
    DOCUMENT_STORAGE_PATH: str = os.getenv("DOCUMENT_STORAGE_PATH", "./data/documents")
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "txt", "hl7", "xml", "json"]
    
    # Features
    ENABLE_OCR: bool = True
    ENABLE_HL7_PARSING: bool = True
    ENABLE_FHIR_PARSING: bool = True
    
    # OCR Configuration
    TESSERACT_LANG: str = "fra+eng"
    TESSERACT_CONFIG: str = "--psm 1"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "*"]
    
    # Processing
    WORKERS: int = 4
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


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
    
    # Database
    DATABASE_URL: str = "postgresql://docqa_admin:changeme@postgres:5432/doc_ingestor"
    
    # RabbitMQ
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "docqa_rabbitmq"
    RABBITMQ_PASS: str = "changeme"
    RABBITMQ_QUEUE: str = "document_processing"
    
    # File Storage
    DOCUMENT_STORAGE_PATH: str = "/data/documents"
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
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Processing
    WORKERS: int = 4
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

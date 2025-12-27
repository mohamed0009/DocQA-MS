"""
Configuration management for DeID service
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Service
    SERVICE_NAME: str = "deid"
    LOG_LEVEL: str = "INFO"
    
    # Eureka Service Discovery
    EUREKA_SERVER_URL: str = os.getenv("EUREKA_SERVER_URL", "http://localhost:8761/eureka")
    ENABLE_EUREKA: bool = os.getenv("ENABLE_EUREKA", "true").lower() == "true"
    INSTANCE_HOST: str = os.getenv("INSTANCE_HOST", "localhost")
    
    # Database - Using SQLite for local development
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./deid.db")
    
    # RabbitMQ (optional for local dev)
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"
    RABBITMQ_CONSUME_QUEUE: str = "document_processing"
    RABBITMQ_PUBLISH_QUEUE: str = "anonymized_documents"
    
    # De-identification Strategy
    DEID_STRATEGY: str = "redact"  # redact, replace, hash, synthesize
    DEID_CONFIDENCE_THRESHOLD: float = 0.85
    
    # spaCy Configuration
    SPACY_MODEL: str = "en_core_web_lg"
    
    # Presidio Configuration
    PRESIDIO_SUPPORTED_LANGUAGES: List[str] = ["en", "fr"]
    
    # Entity Types to Detect
    PII_ENTITIES: List[str] = [
        "PERSON",           # Names
        "PATIENT_ID",       # Patient identifiers
        "SSN",              # Social Security Numbers
        "PHONE_NUMBER",     # Phone numbers
        "EMAIL_ADDRESS",    # Email addresses
        "LOCATION",         # Addresses, cities
        "DATE_TIME",        # Dates and times
        "AGE",              # Ages
        "ID",               # Generic IDs
        "MEDICAL_LICENSE",  # Medical license numbers
    ]
    
    # Medical Entities to Preserve
    PRESERVE_ENTITIES: List[str] = [
        "DISEASE",
        "MEDICATION",
        "PROCEDURE",
        "ANATOMY",
        "SYMPTOM",
    ]
    
    # Synthetic Data Generation
    ENABLE_SYNTHETIC_DATA: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "*"]
    
    # Processing
    WORKERS: int = 4
    BATCH_SIZE: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Gateway settings
    app_name: str = "MedBot API Gateway"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Eureka Service Discovery
    eureka_server_url: str = os.getenv("EUREKA_SERVER_URL", "http://localhost:8761/eureka")
    enable_eureka: bool = os.getenv("ENABLE_EUREKA", "true").lower() == "true"
    service_name: str = "API-GATEWAY"
    instance_host: str = os.getenv("INSTANCE_HOST", "localhost")
    
    # Service URLs - Use localhost for local development
    doc_ingestor_url: str = os.getenv("DOC_INGESTOR_URL", "http://localhost:8002")
    deid_url: str = os.getenv("DEID_URL", "http://localhost:8003")
    indexeur_semantique_url: str = os.getenv("INDEXEUR_SEMANTIQUE_URL", "http://localhost:8001")
    llm_qa_url: str = os.getenv("LLM_QA_URL", "http://localhost:8004")
    synthese_comparative_url: str = os.getenv("SYNTHESE_COMPARATIVE_URL", "http://localhost:8005")
    audit_logger_url: str = os.getenv("AUDIT_LOGGER_URL", "http://localhost:8006")
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000", "*"]
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


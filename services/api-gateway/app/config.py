from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Gateway settings
    app_name: str = "MedBot API Gateway"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Service URLs
    doc_ingestor_url: str = "http://doc-ingestor:8001"
    deid_url: str = "http://deid:8002"
    indexeur_semantique_url: str = "http://indexeur-semantique:8003"
    llm_qa_url: str = "http://llm-qa-module:8004"
    synthese_comparative_url: str = "http://synthese-comparative:8005"
    audit_logger_url: str = "http://audit-logger:8006"
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()

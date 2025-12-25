"""Configuration for SyntheseComparative"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    SERVICE_NAME: str = "synthese-comparative"
    LOG_LEVEL: str = "INFO"
    
    # Database - Using SQLite for local development
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./synthese.db")
    
    # LLM Configuration
    LLM_PROVIDER: str = "ollama"  # ollama or openai
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = "mistral"
    
    # Services URLs - Use localhost for local development
    LLM_QA_SERVICE_URL: str = os.getenv("LLM_QA_SERVICE_URL", "http://localhost:8004")
    SEARCH_SERVICE_URL: str = os.getenv("SEARCH_SERVICE_URL", "http://localhost:8003")
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()


"""Configuration"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    SERVICE_NAME: str = "audit-logger"
    LOG_LEVEL: str = "INFO"
    
    # Eureka Service Discovery
    EUREKA_SERVER_URL: str = os.getenv("EUREKA_SERVER_URL", "http://localhost:8761/eureka")
    ENABLE_EUREKA: bool = os.getenv("ENABLE_EUREKA", "true").lower() == "true"
    INSTANCE_HOST: str = os.getenv("INSTANCE_HOST", "localhost")
    # Database - Using SQLite for local development
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./audit.db")
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "*"]
    
    class Config:
        env_file = ".env"

settings = Settings()


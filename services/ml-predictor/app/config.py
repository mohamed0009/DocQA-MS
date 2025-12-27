"""
Configuration management for ML Predictor service
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Service
    SERVICE_NAME: str = "ml-predictor"
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8007
    
    # Eureka Service Discovery
    EUREKA_SERVER_URL: str = os.getenv("EUREKA_SERVER_URL", "http://localhost:8761/eureka")
    ENABLE_EUREKA: bool = os.getenv("ENABLE_EUREKA", "true").lower() == "true"
    INSTANCE_HOST: str = os.getenv("INSTANCE_HOST", "localhost")
    
    # Database - Using SQLite for local development
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ml_predictor.db")
    
    # RabbitMQ (optional for local dev)
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"
    RABBITMQ_PREDICTION_QUEUE: str = "ml_predictions"
    
    # Model Configuration - Use relative path for local development
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./trained_models")
    READMISSION_MODEL_FILE: str = "readmission_model.pkl"
    PROGRESSION_MODEL_FILE: str = "progression_model.pkl"
    FEATURE_ENGINEER_FILE: str = "feature_engineer.pkl"
    
    # Feature Engineering
    MAX_TEXT_LENGTH: int = 5000
    TFIDF_MAX_FEATURES: int = 100
    TFIDF_MIN_DF: int = 2
    TFIDF_MAX_DF: float = 0.8
    
    # Model Parameters
    PREDICTION_THRESHOLD_LOW: float = 0.3
    PREDICTION_THRESHOLD_HIGH: float = 0.7
    CONFIDENCE_THRESHOLD: float = 0.6
    
    # XGBoost Training Parameters
    XGBOOST_N_ESTIMATORS: int = 300
    XGBOOST_MAX_DEPTH: int = 8
    XGBOOST_LEARNING_RATE: float = 0.05
    XGBOOST_MIN_CHILD_WEIGHT: int = 3
    XGBOOST_SUBSAMPLE: float = 0.8
    XGBOOST_COLSAMPLE_BYTREE: float = 0.8
    XGBOOST_RANDOM_STATE: int = 42
    
    # Training Configuration
    TRAIN_TEST_SPLIT: float = 0.2
    VALIDATION_SPLIT: float = 0.15
    CV_FOLDS: int = 5
    RANDOM_STATE: int = 42
    
    # Hyperparameter Optimization
    BAYESIAN_OPT_ITERATIONS: int = 50
    BAYESIAN_OPT_INIT_POINTS: int = 10
    
    # SHAP Configuration
    SHAP_SAMPLE_SIZE: int = 100
    SHAP_TOP_FEATURES: int = 10
    
    # Performance
    BATCH_SIZE: int = 32
    MAX_WORKERS: int = 4
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,*"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


settings = Settings()


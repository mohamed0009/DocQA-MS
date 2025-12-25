"""
Configuration management for LLM QA Module
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Service
    SERVICE_NAME: str = "llm-qa-module"
    LOG_LEVEL: str = "INFO"
    
    # Database - Using SQLite for local development
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./llm_qa.db")
    
    # RabbitMQ (optional for local dev)
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"
    RABBITMQ_CONSUME_QUEUE: str = "indexed_documents"
    
    # LLM Configuration
    LLM_PROVIDER: str = "ollama"  # ollama, openai, anthropic, local
    
    # Ollama Configuration - Use localhost for local development
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = "mistral"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 1024
    LLM_CONTEXT_LENGTH: int = 4096
    LLM_REQUEST_TIMEOUT: int = 60
    
    # OpenAI Configuration (Fallback or Primary)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    ENABLE_LLM_FALLBACK: bool = False
    
    # Anthropic Configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    
    # HuggingFace / Local LLM Configuration (legacy)
    LOCAL_MODEL_NAME: str = "meta-llama/Llama-2-7b-chat-hf"
    LOCAL_MODEL_PATH: str = "./models/llama-2-70b.gguf"
    LOCAL_MODEL_DEVICE: str = "cpu"  # Use CPU for local development
    LOCAL_LLM_GPU_LAYERS: int = 0
    HF_TOKEN: Optional[str] = None
    
    # RAG Configuration
    RETRIEVAL_TOP_K: int = 5  # Number of chunks to retrieve
    RETRIEVAL_MIN_SIMILARITY: float = 0.7
    ENABLE_RERANKING: bool = True
    RERANKING_TOP_K: int = 3
    
    # Prompt Configuration
    SYSTEM_PROMPT: str = """You are a medical AI assistant helping healthcare professionals analyze clinical documents.
Your role is to provide accurate, evidence-based answers based ONLY on the provided context.

Rules:
1. Only answer based on the provided context
2. If information is not in the context, say "I don't have enough information"
3. Always cite your sources with [Source X] notation
4. Be concise but comprehensive
5. Use medical terminology appropriately
6. Never make up information or hallucinate
"""
    
    QUESTION_PROMPT_TEMPLATE: str = """Context from clinical documents:
{context}

Question: {question}

Please provide a detailed answer based on the context above. Include citations [Source X] for each fact."""
    
    # API Configuration
    MAX_QUERY_LENGTH: int = 500
    ENABLE_STREAMING: bool = True
    ENABLE_CITATIONS: bool = True
    
    # Search Service Integration - Use localhost for local development
    SEARCH_SERVICE_URL: str = os.getenv("SEARCH_SERVICE_URL", "http://localhost:8003")
    
    # ML Predictor Integration
    ML_PREDICTOR_SERVICE_URL: str = os.getenv("ML_PREDICTOR_SERVICE_URL", "http://localhost:8007")
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "*"]
    
    # Performance
    WORKERS: int = 4
    CACHE_TTL_SECONDS: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


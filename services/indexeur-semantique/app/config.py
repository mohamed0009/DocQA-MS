"""
Configuration management for IndexeurSémantique service
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Service
    SERVICE_NAME: str = "indexeur-semantique"
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql://docqa_admin:changeme@postgres:5432/indexeur"
    
    # RabbitMQ
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "docqa_rabbitmq"
    RABBITMQ_PASS: str = "changeme"
    RABBITMQ_CONSUME_QUEUE: str = "anonymized_documents"
    RABBITMQ_PUBLISH_QUEUE: str = "indexed_documents"
    
    # Embedding Model Configuration
    EMBEDDING_PROVIDER: str = "sentence-transformers"  # sentence-transformers or ollama
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    # Alternative medical models:
    # "dmis-lab/biobert-base-cased-v1.2" (768 dim)
    # "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract" (768 dim)
    # "sentence-transformers/all-mpnet-base-v2" (768 dim)
    # Ollama models:
    # "nomic-embed-text" (768 dim) - use with EMBEDDING_PROVIDER=ollama
    
    EMBEDDING_DEVICE: str = "cuda"  # or "cpu" for CPU-only
    EMBEDDING_DIMENSION: int = 384  # Depends on model (384 for MiniLM, 768 for BiomedBERT)
    EMBEDDING_MAX_LENGTH: int = 512
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_CACHE_SIZE: int = 1000
    
    # FAISS Configuration
    FAISS_INDEX_TYPE: str = "IndexFlatL2"  # or IndexIVFFlat for large datasets
    FAISS_INDEX_PATH: str = "/data/faiss_indices"
    FAISS_USE_GPU: bool = True
    FAISS_NLIST: int = 100  # For IVFFlat
    FAISS_NPROBE: int = 10  # Search parameter
    
    # Chunking Strategy
    CHUNKING_STRATEGY: str = "paragraph"  # paragraph, section, sliding_window, semantic
    CHUNK_SIZE: int = 512  # tokens
    CHUNK_OVERLAP: int = 50  # tokens
    MIN_CHUNK_SIZE: int = 50
    MAX_CHUNK_SIZE: int = 1000
    
    # Search Configuration
    SEARCH_TOP_K: int = 10
    SIMILARITY_THRESHOLD: float = 0.7
    ENABLE_HYBRID_SEARCH: bool = True
    
    # BM25 (Keyword Search) Configuration
    BM25_INDEX_PATH: str = "/data/bm25_indices"
    BM25_K1: float = 1.5
    BM25_B: float = 0.75
    
    # Hybrid Search Configuration
    HYBRID_SEARCH_MODE: str = "rrf"  # "rrf" or "weighted"
    HYBRID_SEMANTIC_WEIGHT: float = 0.5  # 0-1
    HYBRID_LEXICAL_WEIGHT: float = 0.5  # 0-1
    RRF_K: int = 60  # RRF constant parameter
    
    # Indexing
    INDEX_BATCH_SIZE: int = 100
    WORKERS: int = 4
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

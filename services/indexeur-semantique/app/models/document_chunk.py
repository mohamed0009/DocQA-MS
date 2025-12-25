"""
Database models for IndexeurSémantique service
"""

from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, Float, JSON
from sqlalchemy.sql import func
import uuid

from ..database import Base


class DocumentChunk(Base):
    """Document chunk model for vector storage"""
    
    __tablename__ = "document_chunks"
    
    # Using String for UUID to support both SQLite and PostgreSQL
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Document reference
    document_id = Column(String(36), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    
    # Content
    chunk_text = Column(Text, nullable=False)
    
    # Chunking metadata
    chunking_strategy = Column(String(50), nullable=False)
    start_position = Column(Integer)
    end_position = Column(Integer)
    
    # Embedding
    embedding_model = Column(String(100), nullable=False)
    faiss_index_id = Column(Integer, index=True)  # ID in FAISS index
    
    # Metadata
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    def __repr__(self):
        return f"<DocumentChunk {self.document_id}:{self.chunk_index}>"


class SearchLog(Base):
    """Search query log for analytics"""
    
    __tablename__ = "search_logs"
    
    # Using String for UUID to support both SQLite and PostgreSQL
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Query
    query = Column(Text, nullable=False)
    query_embedding_model = Column(String(100), nullable=False)
    
    # Search parameters
    top_k = Column(Integer, nullable=False)
    similarity_threshold = Column(Float)
    
    # Results - Using JSON instead of JSONB for SQLite compatibility
    results = Column(JSON, nullable=False)  # Array of {chunk_id, score, document_id}
    results_count = Column(Integer)
    
    # Performance
    search_time_ms = Column(Integer)
    embedding_time_ms = Column(Integer)
    
    # User tracking
    user_id = Column(String(100), index=True)
    
    # Audit
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<SearchLog {self.id}>"


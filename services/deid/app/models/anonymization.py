"""
Database models for DeID service
"""

from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, Float, JSON
from sqlalchemy.sql import func
import uuid

from ..database import Base


class AnonymizationLog(Base):
    """Anonymization log model"""
    
    __tablename__ = "anonymization_logs"
    
    # Using String for UUID to support both SQLite and PostgreSQL
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Document reference
    document_id = Column(String(36), nullable=False, index=True)
    
    # Content
    original_content = Column(Text, nullable=False)
    anonymized_content = Column(Text, nullable=False)
    
    # PII entities detected (array of {type, text, start, end, confidence})
    # Using JSON instead of JSONB for SQLite compatibility
    pii_entities = Column(JSON, nullable=False)
    
    # Configuration
    anonymization_strategy = Column(String(50), nullable=False)  # redact, replace, hash
    
    # Performance metrics
    processing_time_ms = Column(Integer)
    entities_count = Column(Integer)
    confidence_avg = Column(Float)
    
    # Audit
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<AnonymizationLog {self.id} ({self.anonymization_strategy})>"


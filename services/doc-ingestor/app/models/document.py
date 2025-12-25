"""
Database models for DocIngestor service
"""

from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, JSON
from sqlalchemy.sql import func
import uuid

from ..database import Base


class Document(Base):
    """Document model"""
    
    __tablename__ = "documents"
    
    # Using String for UUID to support both SQLite and PostgreSQL
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False, unique=True)
    
    # Metadata
    patient_id = Column(String(100), index=True)
    document_date = Column(TIMESTAMP)
    document_type = Column(String(100), index=True)
    author = Column(String(255))
    department = Column(String(100))
    
    # Processing status
    status = Column(String(50), nullable=False, default="pending", index=True)
    processing_error = Column(Text)
    
    # Extracted content
    extracted_text = Column(Text)
    # Using JSON instead of JSONB for SQLite compatibility
    extracted_metadata = Column(JSON)
    
    # Audit fields
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    
    def __repr__(self):
        return f"<Document {self.filename} ({self.file_type})>"


"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class DocumentBase(BaseModel):
    """Base document schema"""
    patient_id: Optional[str] = None
    document_date: Optional[datetime] = None
    document_type: Optional[str] = None
    author: Optional[str] = None
    department: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    pass


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    patient_id: Optional[str] = None
    document_date: Optional[datetime] = None
    document_type: Optional[str] = None
    author: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    content_hash: str
    status: str
    extracted_text: Optional[str] = None
    extracted_metadata: Optional[Dict[str, Any]] = None
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None


class DocumentList(BaseModel):
    """Schema for paginated document list"""
    total: int
    page: int
    page_size: int
    documents: list[DocumentResponse]


class DocumentUploadResponse(BaseModel):
    """Schema for upload response"""
    id: UUID
    filename: str
    file_type: str
    file_size: int
    status: str
    message: str


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    service: str

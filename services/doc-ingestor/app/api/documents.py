"""
API endpoints for document operations
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
from uuid import UUID
from datetime import datetime
import structlog

from ..database import get_db
from ..models.document import Document
from ..schemas.document import (
    DocumentResponse,
    DocumentList,
    DocumentUploadResponse,
    DocumentUpdate
)
from ..services import DocumentProcessor, get_publisher
from ..config import settings

logger = structlog.get_logger()
router = APIRouter()

# Initialize document processor
doc_processor = DocumentProcessor()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    patient_id: Optional[str] = None,
    document_type: Optional[str] = None,
    author: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Upload and process a medical document
    
    - **file**: Document file (PDF, DOCX, TXT, HL7, FHIR)
    - **patient_id**: Optional patient identifier
    - **document_type**: Optional document type classification
    - **author**: Optional document author
    - **department**: Optional department
    """
    
    # Validate file extension
    if not doc_processor.validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Create temporary file path
    file_type = doc_processor.get_file_type(file.filename)
    temp_path = os.path.join(settings.DOCUMENT_STORAGE_PATH, file.filename)
    
    try:
        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(temp_path)
        
        # Validate file size
        if not doc_processor.validate_file_size(file_size):
            os.remove(temp_path)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
        
        # Calculate file hash for deduplication
        content_hash = doc_processor.calculate_file_hash(temp_path)
        
        # Check if document already exists
        existing = db.query(Document).filter(Document.content_hash == content_hash).first()
        if existing:
            os.remove(temp_path)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Document already exists with ID: {existing.id}"
            )
        
        # Create document record
        document = Document(
            filename=file.filename,
            original_filename=file.filename,
            file_type=file_type,
            file_size=file_size,
            file_path=temp_path,
            content_hash=content_hash,
            patient_id=patient_id,
            document_type=document_type,
            author=author,
            department=department,
            status="processing"
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        logger.info("Document uploaded", document_id=str(document.id), filename=file.filename)
        
        # Process document asynchronously
        try:
            extracted_text, metadata = doc_processor.process_document(temp_path, file_type)
            
            # Update document with extracted content
            document.extracted_text = extracted_text
            document.extracted_metadata = metadata
            document.status = "completed"
            
            # Update patient_id if found in metadata
            if not document.patient_id and metadata.get('patient_id'):
                document.patient_id = metadata.get('patient_id')
            
            db.commit()
            
            logger.info("Document processed successfully", document_id=str(document.id))
            
            # Publish to RabbitMQ
            try:
                publisher = get_publisher()
                publisher.publish_document_processed(
                    document_id=str(document.id),
                    document_data={
                        "patient_id": document.patient_id,
                        "document_type": document.document_type,
                        "file_type": file_type,
                        "extracted_text": extracted_text,
                        "metadata": metadata,
                    }
                )
            except Exception as e:
                logger.error("Failed to publish to RabbitMQ", error=str(e))
                # Don't fail the request if messaging fails
            
        except Exception as e:
            logger.error("Document processing failed", document_id=str(document.id), error=str(e))
            document.status = "failed"
            document.processing_error = str(e)
            db.commit()
        
        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            file_type=document.file_type,
            file_size=document.file_size,
            status=document.status,
            message="Document uploaded and processing started" if document.status == "processing" 
                    else "Document processed successfully" if document.status == "completed"
                    else "Document processing failed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Upload failed", filename=file.filename, error=str(e))
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )


@router.get("/", response_model=DocumentList)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    patient_id: Optional[str] = None,
    document_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all documents with pagination and filtering
    
    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    - **patient_id**: Filter by patient ID
    - **document_type**: Filter by document type
    - **status**: Filter by processing status
    """
    
    query = db.query(Document)
    
    # Apply filters
    if patient_id:
        query = query.filter(Document.patient_id == patient_id)
    if document_type:
        query = query.filter(Document.document_type == document_type)
    if status:
        query = query.filter(Document.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    documents = query.order_by(Document.created_at.desc()).offset(offset).limit(page_size).all()
    
    return DocumentList(
        total=total,
        page=page,
        page_size=page_size,
        documents=documents
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific document by ID
    
    - **document_id**: UUID of the document
    """
    
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    update_data: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update document metadata
    
    - **document_id**: UUID of the document
    - **update_data**: Fields to update
    """
    
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(document, field, value)
    
    document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(document)
    
    logger.info("Document updated", document_id=str(document_id))
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a document
    
    - **document_id**: UUID of the document
    """
    
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file from storage
    if os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except Exception as e:
            logger.error("Failed to delete file", file_path=document.file_path, error=str(e))
    
    # Delete database record
    db.delete(document)
    db.commit()
    
    logger.info("Document deleted", document_id=str(document_id))
    
    return None

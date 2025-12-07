from fastapi import APIRouter, UploadFile, File, HTTPException
import httpx
from ..config import get_settings

router = APIRouter()
settings = get_settings()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for processing"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            response = await client.post(
                f"{settings.doc_ingestor_url}/api/v1/documents/upload",
                files=files
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=503, detail="Document service unavailable")


@router.get("/{document_id}")
async def get_document(document_id: int):
    """Get document by ID"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{settings.doc_ingestor_url}/api/v1/documents/{document_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            raise HTTPException(status_code=404, detail="Document not found")


@router.get("/")
async def list_documents(skip: int = 0, limit: int = 100):
    """List all documents"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{settings.doc_ingestor_url}/api/v1/documents/",
                params={"skip": skip, "limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="Document service unavailable")

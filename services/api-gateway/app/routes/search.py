from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import httpx
from ..config import get_settings
from ..services.service_discovery import get_service_discovery

router = APIRouter()
settings = get_settings()
service_discovery = get_service_discovery()


class SearchRequest(BaseModel):
    query: str
    patient_id: int = None
    top_k: int = 10
    threshold: float = 0.7


@router.post("/semantic")
async def semantic_search(request: SearchRequest):
    """Perform semantic search"""
    indexeur_url = service_discovery.get_indexeur_url()
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{indexeur_url}/api/v1/search/search",
                json=request.dict()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="Search service unavailable")


@router.get("/")
async def keyword_search(
    q: str = Query(..., description="Search query"),
    patient_id: int = None,
    limit: int = 20
):
    """Perform keyword search"""
    indexeur_url = service_discovery.get_indexeur_url()
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{indexeur_url}/api/v1/search/",
                params={"q": q, "patient_id": patient_id, "limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="Search service unavailable")


@router.get("/patients")
async def get_patients():
    """Get unique patients from indexed documents"""
    indexeur_url = service_discovery.get_indexeur_url()
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{indexeur_url}/api/v1/search/patients"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="Search service unavailable")


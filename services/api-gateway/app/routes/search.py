from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import httpx
from ..config import get_settings

router = APIRouter()
settings = get_settings()


class SearchRequest(BaseModel):
    query: str
    patient_id: int = None
    top_k: int = 10
    threshold: float = 0.7


@router.post("/semantic")
async def semantic_search(request: SearchRequest):
    """Perform semantic search"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{settings.indexeur_semantique_url}/api/v1/search/semantic",
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
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{settings.indexeur_semantique_url}/api/v1/search/",
                params={"q": q, "patient_id": patient_id, "limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="Search service unavailable")

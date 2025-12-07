from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from typing import List
from ..config import get_settings

router = APIRouter()
settings = get_settings()


class ComparativeRequest(BaseModel):
    document_ids: List[int]
    analysis_type: str = "temporal"  # temporal, differential, evolution


@router.post("/analyze")
async def comparative_analysis(request: ComparativeRequest):
    """Perform comparative analysis on multiple documents"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{settings.synthese_comparative_url}/api/v1/comparative/analyze",
                json=request.dict()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="Comparative analysis service unavailable")


@router.get("/patient/{patient_id}")
async def get_patient_timeline(patient_id: int):
    """Get temporal analysis for a patient"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{settings.synthese_comparative_url}/api/v1/comparative/patient/{patient_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="Comparative analysis service unavailable")

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from typing import List, Optional
from ..config import get_settings

router = APIRouter()
settings = get_settings()


class SummaryRequest(BaseModel):
    patient_id: str


class ComparisonRequest(BaseModel):
    patient_ids: List[str]


@router.post("/summary")
async def generate_summary(request: SummaryRequest):
    """Generate patient summary via synthese-comparative service"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{settings.synthese_comparative_url}/api/v1/synthesis/summary",
                json=request.dict()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=503, 
                detail=f"Synthesis service unavailable: {str(e)}"
            )


@router.post("/compare")
async def compare_patients(request: ComparisonRequest):
    """Compare multiple patients via synthese-comparative service"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{settings.synthese_comparative_url}/api/v1/synthesis/compare",
                json=request.dict()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=503, 
                detail=f"Synthesis service unavailable: {str(e)}"
            )

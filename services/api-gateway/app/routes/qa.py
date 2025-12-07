from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from ..config import get_settings

router = APIRouter()
settings = get_settings()


class QuestionRequest(BaseModel):
    question: str
    patient_id: int = None
    context_limit: int = 5


@router.post("/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question to the LLM QA module"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{settings.llm_qa_url}/api/v1/qa/ask",
                json=request.dict()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="Q&A service unavailable")


@router.get("/history/{patient_id}")
async def get_qa_history(patient_id: int, limit: int = 10):
    """Get Q&A history for a patient"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{settings.llm_qa_url}/api/v1/qa/history/{patient_id}",
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="Q&A service unavailable")

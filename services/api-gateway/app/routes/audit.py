from fastapi import APIRouter, HTTPException, Query
import httpx
from datetime import datetime
from ..config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: str = None,
    action: str = None,
    start_date: datetime = None,
    end_date: datetime = None
):
    """Get audit logs with filtering"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            params = {
                "skip": skip,
                "limit": limit,
            }
            if user_id:
                params["user_id"] = user_id
            if action:
                params["action"] = action
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
                
            response = await client.get(
                f"{settings.audit_logger_url}/api/v1/audit/logs",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="Audit service unavailable")


@router.get("/stats")
async def get_audit_stats():
    """Get audit statistics"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{settings.audit_logger_url}/api/v1/audit/stats"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="Audit service unavailable")

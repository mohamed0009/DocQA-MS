from fastapi import APIRouter
import httpx
from ..config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check():
    """Check health of all services"""
    services = {
        "doc-ingestor": settings.doc_ingestor_url,
        "deid": settings.deid_url,
        "indexeur-semantique": settings.indexeur_semantique_url,
        "llm-qa": settings.llm_qa_url,
        "synthese-comparative": settings.synthese_comparative_url,
        "audit-logger": settings.audit_logger_url,
    }
    
    health_status = {}
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, service_url in services.items():
            try:
                response = await client.get(f"{service_url}/health")
                health_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "code": response.status_code
                }
            except Exception as e:
                health_status[service_name] = {
                    "status": "unreachable",
                    "error": str(e)
                }
    
    return {
        "gateway": "healthy",
        "services": health_status
    }

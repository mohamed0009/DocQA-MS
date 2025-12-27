"""
Service Discovery module for API Gateway
Handles dynamic service URL resolution via Eureka
"""
import logging
from functools import lru_cache
from typing import Optional
import sys
import os

# Add parent directory to path for shared module import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../shared'))

try:
    from eureka_client import EurekaServiceDiscovery
    EUREKA_AVAILABLE = True
except ImportError:
    EUREKA_AVAILABLE = False
    logging.warning("Eureka client not available. Using fallback URLs only.")

from app.config import get_settings

logger = logging.getLogger(__name__)


class ServiceDiscovery:
    """
    Service discovery helper with Eureka integration and fallback
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.use_eureka = self.settings.enable_eureka and EUREKA_AVAILABLE
        
        # Service name to fallback URL mapping
        self.fallback_urls = {
            "DOC-INGESTOR": self.settings.doc_ingestor_url,
            "DEID": self.settings.deid_url,
            "INDEXEUR-SEMANTIQUE": self.settings.indexeur_semantique_url,
            "LLM-QA-MODULE": self.settings.llm_qa_url,
            "SYNTHESE-COMPARATIVE": self.settings.synthese_comparative_url,
            "AUDIT-LOGGER": self.settings.audit_logger_url,
        }
    
    @lru_cache(maxsize=128)
    def get_service_url(self, service_name: str) -> str:
        """
        Get service URL with Eureka discovery and fallback
        
        Args:
            service_name: Name of the service (e.g., 'DOC-INGESTOR')
            
        Returns:
            Service URL
        """
        service_name_upper = service_name.upper()
        fallback_url = self.fallback_urls.get(service_name_upper)
        
        if not self.use_eureka:
            logger.debug(f"Using fallback URL for {service_name}: {fallback_url}")
            return fallback_url
        
        try:
            # Try Eureka discovery
            url = EurekaServiceDiscovery.get_service_url(
                service_name=service_name_upper,
                fallback_url=fallback_url,
                eureka_server_url=self.settings.eureka_server_url
            )
            return url
        except Exception as e:
            logger.error(f"Error discovering {service_name}: {e}. Using fallback.")
            return fallback_url
    
    def get_doc_ingestor_url(self) -> str:
        """Get Document Ingestor service URL"""
        return self.get_service_url("DOC-INGESTOR")
    
    def get_deid_url(self) -> str:
        """Get De-identification service URL"""
        return self.get_service_url("DEID")
    
    def get_indexeur_url(self) -> str:
        """Get Semantic Indexer service URL"""
        return self.get_service_url("INDEXEUR-SEMANTIQUE")
    
    def get_llm_qa_url(self) -> str:
        """Get LLM Q&A service URL"""
        return self.get_service_url("LLM-QA-MODULE")
    
    def get_synthese_url(self) -> str:
        """Get Comparative Synthesis service URL"""
        return self.get_service_url("SYNTHESE-COMPARATIVE")
    
    def get_audit_url(self) -> str:
        """Get Audit Logger service URL"""
        return self.get_service_url("AUDIT-LOGGER")


# Global instance
_service_discovery: Optional[ServiceDiscovery] = None


def get_service_discovery() -> ServiceDiscovery:
    """Get or create service discovery singleton"""
    global _service_discovery
    if _service_discovery is None:
        _service_discovery = ServiceDiscovery()
    return _service_discovery

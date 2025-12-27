"""
Shared Eureka Client utility for MedBot microservices
Handles service registration, heartbeat, and discovery
"""
import os
import logging
from typing import Optional, List
import py_eureka_client.eureka_client as eureka_client
from py_eureka_client.eureka_client import EurekaServerConf

logger = logging.getLogger(__name__)


class EurekaServiceRegistry:
    """
    Wrapper for Eureka client with MedBot-specific configuration
    """
    
    def __init__(
        self,
        service_name: str,
        service_port: int,
        eureka_server_url: str = None,
        instance_host: str = None,
        health_check_url: str = None,
        enable_eureka: bool = True
    ):
        """
        Initialize Eureka client
        
        Args:
            service_name: Name of the service (e.g., 'api-gateway')
            service_port: Port the service runs on
            eureka_server_url: Eureka server URL (default: http://localhost:8761/eureka)
            instance_host: Host IP/name (auto-detected if None)
            health_check_url: Health check endpoint (default: /health)
            enable_eureka: Enable/disable Eureka registration
        """
        self.service_name = service_name.upper()
        self.service_port = service_port
        self.eureka_server_url = eureka_server_url or os.getenv(
            "EUREKA_SERVER_URL", 
            "http://localhost:8761/eureka"
        )
        self.instance_host = instance_host or self._get_instance_host()
        self.health_check_url = health_check_url or f"http://{self.instance_host}:{service_port}/health"
        self.enable_eureka = enable_eureka and os.getenv("ENABLE_EUREKA", "true").lower() == "true"
        self.registered = False
        
    def _get_instance_host(self) -> str:
        """Get instance host from environment or use localhost"""
        return os.getenv("INSTANCE_HOST", os.getenv("HOSTNAME", "localhost"))
    
    def register(self):
        """Register service with Eureka"""
        if not self.enable_eureka:
            logger.info(f"Eureka disabled for {self.service_name}. Skipping registration.")
            return
            
        try:
            logger.info(f"Registering {self.service_name} with Eureka at {self.eureka_server_url}")
            
            eureka_client.init(
                eureka_server=self.eureka_server_url,
                app_name=self.service_name,
                instance_port=self.service_port,
                instance_host=self.instance_host,
                health_check_url=self.health_check_url,
                # Send heartbeat every 30 seconds
                renewal_interval_in_secs=30,
                # If no heartbeat for 90 seconds, evict instance
                duration_in_secs=90,
            )
            
            self.registered = True
            logger.info(f"✓ {self.service_name} successfully registered with Eureka")
            
        except Exception as e:
            logger.error(f"Failed to register {self.service_name} with Eureka: {e}")
            logger.warning("Service will continue without service discovery")
    
    def deregister(self):
        """Deregister service from Eureka"""
        if not self.enable_eureka or not self.registered:
            return
            
        try:
            logger.info(f"Deregistering {self.service_name} from Eureka")
            eureka_client.stop()
            self.registered = False
            logger.info(f"✓ {self.service_name} deregistered from Eureka")
        except Exception as e:
            logger.error(f"Error deregistering {self.service_name}: {e}")


class EurekaServiceDiscovery:
    """
    Helper for discovering services via Eureka
    """
    
    @staticmethod
    def get_service_url(
        service_name: str, 
        fallback_url: str = None,
        eureka_server_url: str = None
    ) -> str:
        """
        Get service URL from Eureka or fallback to config
        
        Args:
            service_name: Name of the service to discover
            fallback_url: URL to use if Eureka unavailable
            eureka_server_url: Eureka server URL
            
        Returns:
            Service URL (from Eureka or fallback)
        """
        enable_eureka = os.getenv("ENABLE_EUREKA", "true").lower() == "true"
        
        if not enable_eureka:
            logger.debug(f"Eureka disabled, using fallback URL for {service_name}")
            return fallback_url
        
        try:
            # Try to get service instance from Eureka
            service_name_upper = service_name.upper()
            instances = eureka_client.get_applications().get_application(service_name_upper)
            
            if instances and len(instances.instances) > 0:
                # Simple round-robin: get first available instance
                # In production, consider more sophisticated load balancing
                instance = instances.instances[0]
                service_url = f"http://{instance.ipAddr}:{instance.port.port}"
                logger.debug(f"Discovered {service_name} at {service_url} via Eureka")
                return service_url
            else:
                logger.warning(f"No instances found for {service_name} in Eureka")
                
        except Exception as e:
            logger.warning(f"Error discovering {service_name} via Eureka: {e}")
        
        # Fallback to configured URL
        if fallback_url:
            logger.debug(f"Using fallback URL for {service_name}: {fallback_url}")
            return fallback_url
        else:
            raise ValueError(f"No URL available for service {service_name}")
    
    @staticmethod
    def get_all_instances(service_name: str) -> List[dict]:
        """
        Get all instances of a service from Eureka
        
        Args:
            service_name: Name of the service
            
        Returns:
            List of instance dictionaries with host, port, status
        """
        try:
            service_name_upper = service_name.upper()
            app = eureka_client.get_applications().get_application(service_name_upper)
            
            if app and app.instances:
                return [
                    {
                        "host": inst.ipAddr,
                        "port": inst.port.port,
                        "status": inst.status,
                        "instance_id": inst.instanceId
                    }
                    for inst in app.instances
                ]
        except Exception as e:
            logger.error(f"Error getting instances for {service_name}: {e}")
        
        return []

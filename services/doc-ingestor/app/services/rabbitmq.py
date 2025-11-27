"""
RabbitMQ client for publishing document processing events
"""

import pika
import json
import structlog
from typing import Dict, Any

from ..config import settings

logger = structlog.get_logger()


class RabbitMQPublisher:
    """RabbitMQ message publisher"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASS
            )
            
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue
            self.channel.queue_declare(
                queue=settings.RABBITMQ_QUEUE,
                durable=True
            )
            
            logger.info("Connected to RabbitMQ", host=settings.RABBITMQ_HOST)
            
        except Exception as e:
            logger.error("Failed to connect to RabbitMQ", error=str(e))
            raise
    
    def publish_document_processed(self, document_id: str, document_data: Dict[str, Any]):
        """
        Publish document processed event
        
        Args:
            document_id: UUID of processed document
            document_data: Document metadata and content
        """
        try:
            message = {
                "event": "document_processed",
                "document_id": document_id,
                "data": document_data,
            }
            
            self.channel.basic_publish(
                exchange='',
                routing_key=settings.RABBITMQ_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent message
                    content_type='application/json',
                )
            )
            
            logger.info("Published document_processed event", document_id=document_id)
            
        except Exception as e:
            logger.error("Failed to publish message", document_id=document_id, error=str(e))
            # Attempt to reconnect
            self._connect()
            raise
    
    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Closed RabbitMQ connection")


# Global publisher instance
_publisher = None


def get_publisher() -> RabbitMQPublisher:
    """Get RabbitMQ publisher singleton"""
    global _publisher
    if _publisher is None:
        _publisher = RabbitMQPublisher()
    return _publisher

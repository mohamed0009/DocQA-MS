"""
RabbitMQ consumer for processing documents from DocIngestor
"""

import pika
import json
import structlog
from typing import Dict, Any
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .models.anonymization import AnonymizationLog
from .analyzers import get_analyzer
from .services import get_anonymizer

logger = structlog.get_logger()


class RabbitMQConsumer:
    """RabbitMQ consumer for document anonymization"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.analyzer = get_analyzer()
        self.anonymizer = get_anonymizer()
    
    def connect(self):
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
            
            # Declare consume queue
            self.channel.queue_declare(
                queue=settings.RABBITMQ_CONSUME_QUEUE,
                durable=True
            )
            
            # Declare publish queue
            self.channel.queue_declare(
                queue=settings.RABBITMQ_PUBLISH_QUEUE,
                durable=True
            )
            
            logger.info(
                "Connected to RabbitMQ",
                host=settings.RABBITMQ_HOST,
                consume_queue=settings.RABBITMQ_CONSUME_QUEUE
            )
            
        except Exception as e:
            logger.error("Failed to connect to RabbitMQ", error=str(e))
            raise
    
    def process_document(self, document_data: Dict[str, Any], db: Session):
        """
        Process and anonymize a document
        
        Args:
            document_data: Document data from DocIngestor
            db: Database session
        """
        try:
            document_id = document_data.get("document_id")
            extracted_text = document_data.get("extracted_text", "")
            
            if not extracted_text:
                logger.warning("No text to anonymize", document_id=document_id)
                return None
            
            logger.info("Processing document for anonymization", document_id=document_id)
            
            # Detect PII entities
            pii_entities = self.analyzer.analyze(extracted_text, language="en")
            
            # Detect and preserve medical entities
            medical_entities = self.analyzer.detect_medical_entities(extracted_text)
            
            # Filter out medical entities from PII
            pii_entities = [
                e for e in pii_entities
                if not any(
                    m["start"] <= e["start"] < m["end"] or
                    m["start"] < e["end"] <= m["end"]
                    for m in medical_entities
                )
            ]
            
            # Anonymize
            print(f"DEBUG: Starting anonymization with strategy {settings.DEID_STRATEGY}")
            anonymized_text, metadata = self.anonymizer.anonymize(
                text=extracted_text,
                entities=pii_entities,
                strategy=settings.DEID_STRATEGY
            )
            print("DEBUG: Anonymization complete")
            
            # Save to database
            print("DEBUG: Saving to DB (SKIPPED)")
            # log = AnonymizationLog(
            #     document_id=document_id,
            #     original_content=extracted_text,
            #     anonymized_content=anonymized_text,
            #     pii_entities=pii_entities,
            #     anonymization_strategy=settings.DEID_STRATEGY,
            #     entities_count=len(pii_entities),
            #     confidence_avg=sum(e["confidence"] for e in pii_entities) / len(pii_entities) if pii_entities else 0
            # )
            # db.add(log)
            # db.commit()
            print("DEBUG: DB Saved (SKIPPED)")
            
            logger.info(
                "Document anonymized successfully",
                document_id=document_id,
                entities_found=len(pii_entities)
            )
            
            # Prepare message for next service
            return {
                "document_id": document_id,
                "original_text": extracted_text,
                "anonymized_text": anonymized_text,
                "pii_entities": pii_entities,
                "medical_entities": medical_entities,
                "metadata": document_data.get("metadata", {}),
                "patient_id": document_data.get("patient_id"),
                "document_type": document_data.get("document_type")
            }
            
        except Exception as e:
            logger.error("Document processing failed", document_id=document_id, error=str(e))
            raise
    
    def publish_anonymized_document(self, data: Dict[str, Any]):
        """Publish anonymized document to next queue"""
        try:
            message = {
                "event": "document_anonymized",
                "data": data
            }
            
            self.channel.basic_publish(
                exchange='',
                routing_key=settings.RABBITMQ_PUBLISH_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json'
                )
            )
            
            logger.info(
                "Published anonymized document",
                document_id=data.get("document_id")
            )
            
        except Exception as e:
            logger.error("Failed to publish message", error=str(e))
            raise
    
    def callback(self, ch, method, properties, body):
        """Callback for processing messages"""
        db = SessionLocal()
        
        try:
            # Parse message
            message = json.loads(body)
            event = message.get("event")
            
            if event == "document_processed":
                document_data = message.get("data", {})
                
                # Process document
                result = self.process_document(document_data, db)
                
                if result:
                    # Publish to next service
                    self.publish_anonymized_document(result)
                
                # Acknowledge message
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            else:
                logger.warning("Unknown event type", event=event)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
        except Exception as e:
            logger.error("Message processing failed", error=str(e))
            # Reject and requeue message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
        finally:
            db.close()
    
    def start_consuming(self):
        """Start consuming messages"""
        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=settings.RABBITMQ_CONSUME_QUEUE,
                on_message_callback=self.callback
            )
            
            logger.info("Started consuming messages")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.stop()
        except Exception as e:
            logger.error("Consumer error", error=str(e))
            raise
    
    def stop(self):
        """Stop consuming and close connection"""
        if self.channel:
            self.channel.stop_consuming()
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        logger.info("Consumer stopped")


def start_consumer():
    """Start the RabbitMQ consumer"""
    consumer = RabbitMQConsumer()
    consumer.connect()
    consumer.start_consuming()


if __name__ == "__main__":
    start_consumer()

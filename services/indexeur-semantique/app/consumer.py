"""
RabbitMQ consumer for automatic document indexing
"""

import pika
import json
import structlog
from typing import Dict, Any
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .models.document_chunk import DocumentChunk
from .services import get_chunker, get_faiss_manager
from .embeddings import get_embedding_generator

logger = structlog.get_logger()


class RabbitMQConsumer:
    """RabbitMQ consumer for document indexing"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.chunker = get_chunker()
        self.embedding_generator = get_embedding_generator()
        self.faiss_manager = get_faiss_manager()
    
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
            
            # Declare queues
            self.channel.queue_declare(
                queue=settings.RABBITMQ_CONSUME_QUEUE,
                durable=True
            )
            
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
    
    def index_document(self, document_data: Dict[str, Any], db: Session):
        """Index a document for semantic search"""
        
        try:
            document_id = document_data.get("document_id")
            # Use anonymized text if available
            text = document_data.get("anonymized_text") or document_data.get("original_text", "")
            
            if not text:
                logger.warning("No text to index", document_id=document_id)
                return None
            
            logger.info("Indexing document", document_id=document_id)
            
            # Chunk text
            chunks = self.chunker.chunk_text(text, settings.CHUNKING_STRATEGY)
            
            if not chunks:
                logger.warning("No chunks generated", document_id=document_id)
                return None
            
            # Generate embeddings
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedding_generator.generate_embeddings_batch(chunk_texts)
            
            # Save to database and FAISS
            chunk_metadata = []
            chunk_ids = []
            
            for chunk in chunks:
                db_chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk["index"],
                    chunk_text=chunk["text"],
                    chunking_strategy=settings.CHUNKING_STRATEGY,
                    start_position=chunk.get("start"),
                    end_position=chunk.get("end"),
                    embedding_model=settings.EMBEDDING_MODEL
                )
                db.add(db_chunk)
                db.flush()
                
                chunk_metadata.append({
                    "chunk_id": str(db_chunk.id),
                    "document_id": str(document_id),
                    "chunk_index": chunk["index"],
                    "chunk_text": chunk["text"]
                })
                chunk_ids.append(db_chunk.id)
            
            # Add to FAISS
            faiss_ids = self.faiss_manager.add_vectors(embeddings, chunk_metadata)
            
            # Update FAISS IDs
            for chunk_id, faiss_id in zip(chunk_ids, faiss_ids):
                db.query(DocumentChunk).filter(
                    DocumentChunk.id == chunk_id
                ).update({"faiss_index_id": faiss_id})
            
            db.commit()
            
            logger.info(
                "Document indexed successfully",
                document_id=document_id,
                chunks=len(chunks)
            )
            
            return {
                "document_id": document_id,
                "chunks_created": len(chunks),
                "faiss_ids": faiss_ids,
                "metadata": document_data.get("metadata", {})
            }
            
        except Exception as e:
            logger.error("Indexing failed", document_id=document_id, error=str(e))
            raise
    
    def publish_indexed_document(self, data: Dict[str, Any]):
        """Publish indexed document to next queue"""
        try:
            message = {
                "event": "document_indexed",
                "data": data
            }
            
            self.channel.basic_publish(
                exchange='',
                routing_key=settings.RABBITMQ_PUBLISH_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            logger.info("Published indexed document", document_id=data.get("document_id"))
            
        except Exception as e:
            logger.error("Failed to publish message", error=str(e))
            raise
    
    def callback(self, ch, method, properties, body):
        """Callback for processing messages"""
        db = SessionLocal()
        
        try:
            message = json.loads(body)
            event = message.get("event")
            
            if event == "document_anonymized":
                document_data = message.get("data", {})
                
                # Index document
                result = self.index_document(document_data, db)
                
                if result:
                    # Publish to next service
                    self.publish_indexed_document(result)
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            else:
                logger.warning("Unknown event type", event=event)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
        except Exception as e:
            logger.error("Message processing failed", error=str(e))
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

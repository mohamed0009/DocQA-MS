
import pika
import json

def publish():
    credentials = pika.PlainCredentials('docqa_rabbitmq', 'changeme')
    parameters = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    queue_name = 'document_processing'
    channel.queue_declare(queue=queue_name, durable=True)
    
    message = {
        "event": "document_processed",
        "data": {
            "document_id": "TEST_DOC_001",
            "extracted_text": "This is a test document for Patient PAT001. Patient name is John Doe.",
            "metadata": {},
            "patient_id": "PAT001",
            "document_type": "clinical_note"
        }
    }
    
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(f"Published test message to {queue_name}")
    connection.close()

if __name__ == "__main__":
    publish()

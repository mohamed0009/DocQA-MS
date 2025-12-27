"""
Bridge script to manually index documents from DocIngestor to IndexeurSemantique
Use this when RabbitMQ is not available for local development.
"""
import requests
import time

DOC_INGESTOR_URL = "http://localhost:8001/api/v1/documents"
INDEXER_URL = "http://localhost:8003/api/v1/search/index"

def index_documents():
    print("Fetching documents from DocIngestor...")
    # Fetch all documents (up to 100 for now)
    try:
        response = requests.get(f"{DOC_INGESTOR_URL}?page_size=100")
        response.raise_for_status()
        data = response.json()
        documents = data.get("documents", [])
        
        print(f"Found {len(documents)} documents. Starting indexing...")
        
        success_count = 0
        skip_count = 0
        
        for doc in documents:
            doc_id = doc["id"]
            text = doc.get("extracted_text")
            status = doc.get("status")
            patient_id = doc.get("patient_id")
            
            if status != "completed" or not text:
                print(f"Skipping {doc['filename']} (Status: {status}, Text len: {len(text) if text else 0})")
                skip_count += 1
                continue
                
            # Prepare indexing payload
            payload = {
                "document_id": doc_id,
                "text": text,
                "chunking_strategy": "paragraph",
                "metadata": {
                    "patient_id": patient_id,
                    "document_type": doc.get("document_type"),
                    "author": doc.get("author"),
                    "created_at": doc.get("created_at")
                }
            }
            
            try:
                idx_response = requests.post(INDEXER_URL, json=payload)
                idx_response.raise_for_status()
                print(f"✓ Indexed: {doc['filename']} for {patient_id}")
                success_count += 1
                time.sleep(0.2)
            except Exception as e:
                print(f"✗ Failed to index {doc['filename']}: {e}")
                
        print(f"\nIndexing Complete!")
        print(f"Successfully indexed: {success_count}")
        print(f"Skipped: {skip_count}")
        
    except Exception as e:
        print(f"Error fetching documents: {e}")

if __name__ == "__main__":
    index_documents()

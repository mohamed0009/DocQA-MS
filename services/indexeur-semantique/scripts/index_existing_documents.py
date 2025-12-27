"""
Script to index existing documents from doc-ingestor into FAISS

This script reads documents from the doc-ingestor database and indexes them
into FAISS via the indexing API.
"""

import os
import sys
import requests
import time

print("📚 Indexing Script for Existing Documents")
print("=" * 50)

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
indexeur_dir = os.path.dirname(script_dir)
services_dir = os.path.dirname(indexeur_dir)
doc_ingestor_dir = os.path.join(services_dir, 'doc-ingestor')
doc_ingestor_db = os.path.join(doc_ingestor_dir, "doc_ingestor.db")

if not os.path.exists(doc_ingestor_db):
    print(f"❌ doc_ingestor.db not found at: {doc_ingestor_db}")
    sys.exit(1)

# Add doc-ingestor to path
sys.path.insert(0, doc_ingestor_dir)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Connect to database
engine = create_engine(f'sqlite:///{doc_ingestor_db}')
Session = sessionmaker(bind=engine)
db_session = Session()

# Query completed documents with extracted text
result = db_session.execute(text(
    'SELECT id, filename, extracted_text, patient_id FROM documents WHERE status = "completed" AND extracted_text IS NOT NULL'
))
documents = result.fetchall()

print(f"✅ Found {len(documents)} completed documents with text\n")

if len(documents) == 0:
    print("❌ No documents to index")
    db_session.close()
    sys.exit(0)

# Index via API
INDEXER_URL = "http://localhost:8001/api/v1/search/index"
indexed_count = 0
failed_count = 0
total_chunks = 0

for doc_id, filename, extracted_text, patient_id in documents:
    # Skip if text is too short
    if len(extracted_text.strip()) < 50:
        print(f"⚠️  Skipping {filename} - text too short")
        continue
    
    print(f"📄 Indexing: {filename[:50]}...")
    
    try:
        # Prepare request
        payload = {
            "document_id": str(doc_id),
            "text": extracted_text[:10000],  # Limit text length for speed
            "chunking_strategy": "paragraph",
            "metadata": {}
        }
        
        if patient_id:
            payload["metadata"]["patient_id"] = patient_id
        
        # Call API
        response = requests.post(INDEXER_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            chunks_created = data.get('chunks_created', 0)
            total_chunks += chunks_created
            print(f"   ✅ Created {chunks_created} chunks")
            indexed_count += 1
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            print(f"      {response.text[:150]}")
            failed_count += 1
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout")
        failed_count += 1
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        failed_count += 1
    
    # Small delay to not overwhelm the service
    time.sleep(0.1)

db_session.close()

print(f"\n{'=' * 50}")
print(f"📊 Indexing Complete!")
print(f"   ✅ Documents indexed: {indexed_count}/{len(documents)}")
print(f"   ❌ Failed: {failed_count}")
print(f"   📦 Total chunks created: {total_chunks}")

if indexed_count > 0:
    print(f"\n💡 Next: Run 'python scripts\\add_demo_patients.py' to add patient metadata")


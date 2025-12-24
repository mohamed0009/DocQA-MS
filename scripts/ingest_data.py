import os
import requests
import time
import mimetypes
import argparse
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{API_URL}/api/v1/documents/upload"
DATA_DIR = Path("datasets/medical")
DEFAULT_PATIENT_ID = "PAT_GENERAL"

def ingest_data(directory: Path, patient_id: str):
    print(f"🚀 Starting ingestion from {directory}...")
    
    if not directory.exists():
        print(f"❌ Directory {directory} not found!")
        return

    files = [f for f in directory.glob("**/*") if f.is_file()]
    total_files = len(files)
    print(f"📂 Found {total_files} files to process.")

    success_count = 0
    fail_count = 0

    for i, file_path in enumerate(files, 1):
        filename = file_path.name
        print(f"[{i}/{total_files}] Uploading {filename}...")
        
        try:
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"
            
            with open(file_path, "rb") as f:
                files_payload = {
                    "file": (filename, f, mime_type)
                }
                data_payload = {
                    "patient_id": patient_id
                }
                
                response = requests.post(UPLOAD_ENDPOINT, files=files_payload, data=data_payload)
                
                if response.status_code in [200, 201, 202]:
                    data = response.json()
                    doc_id = data.get("id") or data.get("document_id")
                    print(f"   ✅ Success! ID: {doc_id}")
                    success_count += 1
                else:
                    print(f"   ❌ Failed: {response.status_code} - {response.text}")
                    fail_count += 1
                    
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            fail_count += 1
            
        # Small delay to be nice to the API
        time.sleep(0.5)

    print("\n========================================")
    print("📊 Ingestion Summary")
    print("========================================")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed:     {fail_count}")
    print("========================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MedBot Data Ingestion Tool")
    parser.add_argument("--dir", type=Path, default=DATA_DIR, help="Directory containing medical documents")
    parser.add_argument("--patient", type=str, default=DEFAULT_PATIENT_ID, help="Patient ID to associate with documents")
    
    args = parser.parse_args()
    
    ingest_data(args.dir, args.patient)

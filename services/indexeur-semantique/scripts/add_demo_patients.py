"""
Script to add demo patient metadata to existing FAISS index

This script loads the existing FAISS index and distributes the indexed chunks
across 10 demo patients by adding patient metadata to each chunk.
"""

import os
import sys
import pickle
import random

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

# Demo patients data
DEMO_PATIENTS = [
    {"patient_id": "PAT001", "patient_name": "Ahmed Benali", "patient_age": 45, "patient_gender": "Male"},
    {"patient_id": "PAT002", "patient_name": "Fatima Zahra", "patient_age": 32, "patient_gender": "Female"},
    {"patient_id": "PAT003", "patient_name": "Mohammed Alami", "patient_age": 67, "patient_gender": "Male"},
    {"patient_id": "PAT004", "patient_name": "Sara Idrissi", "patient_age": 28, "patient_gender": "Female"},
    {"patient_id": "PAT005", "patient_name": "Youssef Tahiri", "patient_age": 51, "patient_gender": "Male"},
    {"patient_id": "PAT006", "patient_name": "Amina El Fassi", "patient_age": 39, "patient_gender": "Female"},
    {"patient_id": "PAT007", "patient_name": "Karim Benjelloun", "patient_age": 54, "patient_gender": "Male"},
    {"patient_id": "PAT008", "patient_name": "Laila Tazi", "patient_age": 41, "patient_gender": "Female"},
    {"patient_id": "PAT009", "patient_name": "Omar Chraibi", "patient_age": 62, "patient_gender": "Male"},
    {"patient_id": "PAT010", "patient_name": "Zineb Alaoui", "patient_age": 35, "patient_gender": "Female"},
]


def main():
    """Add demo patient metadata to existing FAISS index"""
    
    # Path to metadata file
    metadata_path = os.path.join(settings.FAISS_INDEX_PATH, "metadata.pkl")
    
    if not os.path.exists(metadata_path):
        print(f"❌ Metadata file not found at: {metadata_path}")
        print("   Make sure the FAISS index has been created and documents have been indexed.")
        return
    
    # Load existing metadata
    print(f"📂 Loading metadata from: {metadata_path}")
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)
    
    id_to_chunk = metadata.get('id_to_chunk', {})
    next_id = metadata.get('next_id', 0)
    
    print(f"✅ Found {len(id_to_chunk)} chunks in the index")
    
    if len(id_to_chunk) == 0:
        print("❌ No chunks found in the index. Please index some documents first.")
        return
    
    # Track how many chunks were updated
    updated_count = 0
    chunks_per_patient = {}
    
    # Distribute chunks across patients
    chunk_ids = list(id_to_chunk.keys())
    random.shuffle(chunk_ids)  # Randomize distribution
    
    chunks_per_patient_target = len(chunk_ids) // len(DEMO_PATIENTS)
    
    patient_idx = 0
    for i, chunk_id in enumerate(chunk_ids):
        # Determine which patient this chunk belongs to
        patient = DEMO_PATIENTS[patient_idx]
        
        # Add patient metadata to the chunk
        id_to_chunk[chunk_id].update({
            "patient_id": patient["patient_id"],
            "patient_name": patient["patient_name"],
            "patient_age": patient["patient_age"],
            "patient_gender": patient["patient_gender"],
        })
        
        updated_count += 1
        
        # Track chunks per patient
        if patient["patient_id"] not in chunks_per_patient:
            chunks_per_patient[patient["patient_id"]] = 0
        chunks_per_patient[patient["patient_id"]] += 1
        
        # Move to next patient (round-robin distribution)
        if (i + 1) % chunks_per_patient_target == 0 and patient_idx < len(DEMO_PATIENTS) - 1:
            patient_idx += 1
    
    # Save updated metadata
    print(f"\n💾 Saving updated metadata...")
    metadata['id_to_chunk'] = id_to_chunk
    
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    
    print(f"✅ Successfully updated {updated_count} chunks with patient metadata")
    
    # Display summary
    print(f"\n📊 Patient Distribution Summary:")
    print(f"{'Patient ID':<12} {'Name':<20} {'Chunks':<10}")
    print("-" * 45)
    for patient in DEMO_PATIENTS:
        patient_id = patient["patient_id"]
        count = chunks_per_patient.get(patient_id, 0)
        print(f"{patient_id:<12} {patient['patient_name']:<20} {count:<10}")
    
    print(f"\n✨ Done! The patients should now appear at http://localhost:3000/patients")
    print(f"   You may need to refresh the page.")


if __name__ == "__main__":
    main()

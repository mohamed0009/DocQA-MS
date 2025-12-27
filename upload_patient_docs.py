"""
Generate sample medical documents for testing - FIXED VERSION
"""
import requests
from datetime import datetime, timedelta
import random

# API endpoint
DOC_INGESTOR_URL = "http://localhost:8001/api/v1/documents/upload"

# Sample medical data templates
PATIENTS = [
    {"id": "PAT001", "name": "John Smith", "age": 45, "gender": "M"},
    {"id": "PAT002", "name": "Sarah Johnson", "age": 32, "gender": "F"},
    {"id": "PAT003", "name": "Michael Chen", "age": 58, "gender": "M"},
    {"id": "PAT004", "name": "Emily Davis", "age": 27, "gender": "F"},
    {"id": "PAT005", "name": "Robert Williams", "age": 63, "gender": "M"},
]

DIAGNOSES = [
    "Type 2 Diabetes Mellitus",
    "Hypertension",
    "Chronic Obstructive Pulmonary Disease",
    "Coronary Artery Disease",
    "Asthma",
    "Hyperlipidemia",
]

MEDICATIONS = [
    "Metformin 500mg bid",
    "Lisinopril 10mg daily",
    "Atorvastatin 20mg daily",
    "Aspirin 81mg daily",
    "Omeprazole 20mg daily",
    "Albuterol inhaler prn",
]

def generate_clinical_note(patient):
    """Generate a clinical note"""
    date = (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
    diagnosis = random.choice(DIAGNOSES)
    meds = random.sample(MEDICATIONS, k=random.randint(2, 4))
    
    content = f"""CLINICAL NOTE

Patient: {patient['name']}
Patient ID: {patient['id']}
Date: {date}
Age: {patient['age']} years
Gender: {patient['gender']}

CHIEF COMPLAINT:
Follow-up visit for chronic condition management.

HISTORY OF PRESENT ILLNESS:
Patient presents for routine follow-up. Reports adherence to medication regimen. 
Denies chest pain, shortness of breath, or other acute concerns.

CURRENT MEDICATIONS:
{chr(10).join(f"- {med}" for med in meds)}

VITAL SIGNS:
Blood Pressure: {random.randint(110, 140)}/{random.randint(70, 90)} mmHg
Heart Rate: {random.randint(60, 90)} bpm
Temperature: {round(random.uniform(36.4, 37.2), 1)}°C
Respiratory Rate: {random.randint(12, 20)} breaths/min
SpO2: {random.randint(95, 100)}%

ASSESSMENT:
{diagnosis} - stable, well controlled

PLAN:
1. Continue current medications
2. Follow up in 3 months
3. Monitor blood pressure at home
4. Lifestyle modifications counseling provided

Dr. Martinez, MD
Internal Medicine
"""
    return content

def generate_lab_report(patient):
    """Generate a lab report"""
    date = (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d")
    
    content = f"""LABORATORY REPORT

Patient: {patient['name']}
Patient ID: {patient['id']}
Date Collected: {date}

COMPLETE BLOOD COUNT:
WBC: {round(random.uniform(4.0, 11.0), 1)} K/uL
Hemoglobin: {round(random.uniform(12.0, 17.0), 1)} g/dL
Platelets: {random.randint(150, 400)} K/uL

METABOLIC PANEL:
Glucose: {random.randint(70, 140)} mg/dL
Creatinine: {round(random.uniform(0.6, 1.3), 2)} mg/dL
Sodium: {random.randint(135, 145)} mmol/L

LIPID PANEL:
Total Cholesterol: {random.randint(120, 240)} mg/dL
LDL: {random.randint(60, 160)} mg/dL
Triglycerides: {random.randint(50, 200)} mg/dL

HbA1c: {round(random.uniform(5.0, 8.5), 1)}%

Dr. Sarah Chen, MD
Clinical Pathology
"""
    return content

def upload_document(content, patient_id, doc_type, filename):
    """Upload a document to the system"""
    try:
        # Create files dict for multipart upload
        files = {
            'file': (filename, content.encode('utf-8'), 'text/plain')
        }
        
        # Send form data correctly
        data = {
            'patient_id': patient_id,
            'document_type': doc_type,
            'author': 'Dr. Martinez',
            'department': 'Internal Medicine'
        }
        
        print(f"Uploading {filename} with patient_id={patient_id}...")
        
        response = requests.post(DOC_INGESTOR_URL, files=files, data=data, timeout=30)
        
        if response.status_code in [200, 201]:
            print(f"✓ Uploaded: {filename} for {patient_id}")
            return True
        else:
            print(f"✗ Failed: {filename} - Status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Error uploading {filename}: {str(e)}")
        return False

def main():
    """Generate and upload sample documents"""
    print("="*60)
    print("Generating Medical Documents with Patient IDs")
    print("="*60)
    print()
    
    success_count = 0
    total_count = 0
    
    for patient in PATIENTS:
        patient_id = patient['id']
        print(f"\n📋 Processing {patient['name']} ({patient_id})...")
        
        # Generate 1-2 clinical notes
        for i in range(random.randint(1, 2)):
            content = generate_clinical_note(patient)
            filename = f"{patient_id}_clinical_note_{i+1}.txt"
            if upload_document(content, patient_id, "clinical_note", filename):
                success_count += 1
            total_count += 1
        
        # Generate 1 lab report
        content = generate_lab_report(patient)
        filename = f"{patient_id}_lab_report.txt"
        if upload_document(content, patient_id, "lab_report", filename):
            success_count += 1
        total_count += 1
    
    print()
    print("="*60)
    print(f"✅ Upload Complete: {success_count}/{total_count} documents")
    print("="*60)
    
    if success_count > 0:
        print("\n🎯 Next Steps:")
        print("  1. Refresh the QA page in your browser")
        print("  2. Patient dropdown should now show: PAT001-PAT005")
        print("  3. Select a patient and ask questions!")

if __name__ == "__main__":
    main()

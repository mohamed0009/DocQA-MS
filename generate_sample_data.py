"""
Generate sample medical documents for testing
"""
import requests
import json
from datetime import datetime, timedelta
import random
from io import BytesIO

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
    "Gastroesophageal Reflux Disease",
    "Osteoarthritis",
]

MEDICATIONS = [
    "Metformin 500mg bid",
    "Lisinopril 10mg daily",
    "Atorvastatin 20mg daily",
    "Aspirin 81mg daily",
    "Omeprazole 20mg daily",
    "Albuterol inhaler prn",
    "Levothyroxine 50mcg daily",
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
Date Reported: {date}

COMPLETE BLOOD COUNT:
WBC: {round(random.uniform(4.0, 11.0), 1)} K/uL (4.0-11.0)
RBC: {round(random.uniform(4.0, 6.0), 2)} M/uL (4.0-6.0)
Hemoglobin: {round(random.uniform(12.0, 17.0), 1)} g/dL (12.0-17.0)
Hematocrit: {round(random.uniform(36.0, 50.0), 1)}% (36.0-50.0)
Platelets: {random.randint(150, 400)} K/uL (150-400)

COMPREHENSIVE METABOLIC PANEL:
Glucose: {random.randint(70, 140)} mg/dL (70-100)
BUN: {random.randint(7, 25)} mg/dL (7-25)
Creatinine: {round(random.uniform(0.6, 1.3), 2)} mg/dL (0.6-1.3)
Sodium: {random.randint(135, 145)} mmol/L (135-145)
Potassium: {round(random.uniform(3.5, 5.0), 1)} mmol/L (3.5-5.0)
Chloride: {random.randint(96, 106)} mmol/L (96-106)

LIPID PANEL:
Total Cholesterol: {random.randint(120, 240)} mg/dL (<200)
LDL: {random.randint(60, 160)} mg/dL (<100)
HDL: {random.randint(40, 80)} mg/dL (>40)
Triglycerides: {random.randint(50, 200)} mg/dL (<150)

HbA1c: {round(random.uniform(5.0, 8.5), 1)}% (<5.7)

INTERPRETATION:
Results reviewed. Patient notified. Follow-up as scheduled.

Electronically signed by:
Dr. Sarah Chen, MD
Clinical Pathology
"""
    return content

def generate_discharge_summary(patient):
    """Generate a discharge summary"""
    admit_date = (datetime.now() - timedelta(days=random.randint(10, 30))).strftime("%Y-%m-%d")
    discharge_date = (datetime.now() - timedelta(days=random.randint(1, 9))).strftime("%Y-%m-%d")
    
    content = f"""DISCHARGE SUMMARY

Patient: {patient['name']}
Patient ID: {patient['id']}
Admission Date: {admit_date}
Discharge Date: {discharge_date}

PRINCIPAL DIAGNOSIS:
{random.choice(DIAGNOSES)}

HOSPITAL COURSE:
Patient admitted through emergency department with acute exacerbation of chronic condition.
Initial treatment included IV fluids and medication adjustment. Patient responded well to
therapy. Vital signs stabilized within 48 hours. Patient ambulatory and tolerating oral intake.

DISCHARGE MEDICATIONS:
{chr(10).join(f"{i+1}. {med}" for i, med in enumerate(random.sample(MEDICATIONS, k=3)))}

DISCHARGE INSTRUCTIONS:
1. Take all medications as prescribed
2. Follow up with primary care physician in 1 week
3. Return to ED if symptoms worsen
4. Maintain low-sodium diet
5. Ambulate regularly, avoid prolonged bed rest

FOLLOW-UP:
Primary care appointment scheduled for {(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")}

Patient discharged in stable condition.

Dr. Robert Williams, MD
Hospitalist
"""
    return content

def upload_document(content, patient_id, doc_type, filename):
    """Upload a document to the system"""
    try:
        # Create a file-like object
        file_content = content.encode('utf-8')
        files = {
            'file': (filename, BytesIO(file_content), 'text/plain')
        }
        
        data = {
            'patient_id': patient_id,
            'document_type': doc_type,
            'author': 'Dr. Martinez',
            'department': 'Internal Medicine'
        }
        
        response = requests.post(DOC_INGESTOR_URL, files=files, data=data)
        
        if response.status_code in [200, 201]:
            print(f"✓ Uploaded: {filename} for {patient_id}")
            return True
        else:
            print(f"✗ Failed to upload {filename}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error uploading {filename}: {str(e)}")
        return False

def main():
    """Generate and upload sample documents"""
    print("Generating sample medical documents...\n")
    
    success_count = 0
    total_count = 0
    
    for patient in PATIENTS:
        patient_id = patient['id']
        
        # Generate 1-2 clinical notes per patient
        for i in range(random.randint(1, 2)):
            content = generate_clinical_note(patient)
            filename = f"{patient_id}_clinical_note_{i+1}.txt"
            if upload_document(content, patient_id, "clinical_note", filename):
                success_count += 1
            total_count += 1
        
        # Generate 1 lab report per patient
        content = generate_lab_report(patient)
        filename = f"{patient_id}_lab_report.txt"
        if upload_document(content, patient_id, "lab_report", filename):
            success_count += 1
        total_count += 1
        
        # Generate discharge summary for some patients
        if random.random() > 0.5:
            content = generate_discharge_summary(patient)
            filename = f"{patient_id}_discharge_summary.txt"
            if upload_document(content, patient_id, "discharge_summary", filename):
                success_count += 1
            total_count += 1
    
    print(f"\n{'='*50}")
    print(f"Generation Complete!")
    print(f"Successfully uploaded: {success_count}/{total_count} documents")
    print(f"{'='*50}")
    
    if success_count > 0:
        print("\n✓ You can now:")
        print("  1. Refresh the QA page")
        print("  2. Select a patient from the dropdown")
        print("  3. Ask questions about their medical records")

if __name__ == "__main__":
    main()

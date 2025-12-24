"""
Generate synthetic patient data for model training

This script creates realistic synthetic patient data including:
- Demographics
- Diagnoses (ICD-10 codes)
- Medications
- Lab values
- Vital signs
- Admission history
- Clinical notes
- Outcome labels (readmission, disease progression)
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import json
from pathlib import Path

# Initialize Faker
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Common ICD-10 codes for chronic conditions
ICD10_CODES = {
    'diabetes': ['E11.9', 'E11.65', 'E11.22', 'E11.40'],
    'hypertension': ['I10', 'I11.9', 'I12.9'],
    'heart_failure': ['I50.9', 'I50.1', 'I50.23'],
    'copd': ['J44.9', 'J44.1', 'J44.0'],
    'ckd': ['N18.3', 'N18.4', 'N18.5'],
    'cad': ['I25.10', 'I25.119', 'I25.700'],
    'stroke': ['I63.9', 'I64', 'I67.9'],
    'pneumonia': ['J18.9', 'J15.9', 'J13']
}

# Common medications
MEDICATIONS = {
    'diabetes': ['metformin', 'insulin glargine', 'glipizide', 'sitagliptin'],
    'hypertension': ['lisinopril', 'amlodipine', 'losartan', 'hydrochlorothiazide'],
    'heart_failure': ['furosemide', 'carvedilol', 'spironolactone', 'digoxin'],
    'copd': ['albuterol', 'tiotropium', 'fluticasone', 'prednisone'],
    'anticoagulants': ['warfarin', 'apixaban', 'rivaroxaban'],
    'statins': ['atorvastatin', 'simvastatin', 'rosuvastatin'],
    'pain': ['acetaminophen', 'ibuprofen', 'tramadol', 'oxycodone']
}


def generate_patient_demographics(n_patients=1000):
    """Generate patient demographics"""
    patients = []
    
    for i in range(n_patients):
        age = np.random.choice(
            [random.randint(18, 45), random.randint(45, 65), random.randint(65, 95)],
            p=[0.2, 0.3, 0.5]  # Skew towards older patients
        )
        
        gender = random.choice(['M', 'F'])
        
        # BMI with realistic distribution
        bmi = np.random.normal(28, 6)
        bmi = max(15, min(50, bmi))  # Clip to reasonable range
        
        patients.append({
            'patient_id': f'PAT{i:05d}',
            'age': age,
            'gender': gender,
            'bmi': round(bmi, 1)
        })
    
    return pd.DataFrame(patients)


def generate_diagnoses(patients_df):
    """Generate diagnoses for patients"""
    diagnoses_data = []
    
    for _, patient in patients_df.iterrows():
        # Number of diagnoses increases with age
        n_diagnoses = min(1 + int(patient['age'] / 20), 8)
        
        # Select random condition categories
        conditions = random.sample(list(ICD10_CODES.keys()), k=min(n_diagnoses, len(ICD10_CODES)))
        
        patient_diagnoses = []
        for condition in conditions:
            # Pick 1-2 codes from each condition
            codes = random.sample(ICD10_CODES[condition], k=min(random.randint(1, 2), len(ICD10_CODES[condition])))
            patient_diagnoses.extend(codes)
        
        diagnoses_data.append({
            'patient_id': patient['patient_id'],
            'diagnoses': patient_diagnoses,
            'primary_diagnosis': patient_diagnoses[0] if patient_diagnoses else None,
            'n_diagnoses': len(patient_diagnoses)
        })
    
    return pd.DataFrame(diagnoses_data)


def generate_medications(patients_df, diagnoses_df):
    """Generate medication lists based on diagnoses"""
    medications_data = []
    
    for _, patient in patients_df.iterrows():
        patient_diagnoses = diagnoses_df[diagnoses_df['patient_id'] == patient['patient_id']]['diagnoses'].iloc[0]
        
        patient_meds = []
        
        # Add medications based on conditions
        for diagnosis in patient_diagnoses:
            for condition, codes in ICD10_CODES.items():
                if diagnosis in codes:
                    # Add 1-2 medications for this condition
                    meds = random.sample(MEDICATIONS.get(condition, []), k=min(random.randint(1, 2), len(MEDICATIONS.get(condition, []))))
                    patient_meds.extend(meds)
        
        # Add some common medications
        if random.random() > 0.5:
            patient_meds.append(random.choice(MEDICATIONS['statins']))
        
        # Remove duplicates
        patient_meds = list(set(patient_meds))
        
        medications_data.append({
            'patient_id': patient['patient_id'],
            'medications': patient_meds,
            'n_medications': len(patient_meds),
            'polypharmacy': len(patient_meds) > 5
        })
    
    return pd.DataFrame(medications_data)


def generate_lab_values(patients_df):
    """Generate realistic lab values"""
    lab_data = []
    
    for _, patient in patients_df.iterrows():
        # Generate lab values with some correlation to age
        age_factor = patient['age'] / 100
        
        labs = {
            'glucose': max(70, np.random.normal(100 + age_factor * 50, 30)),
            'creatinine': max(0.5, np.random.normal(0.9 + age_factor * 0.5, 0.3)),
            'hemoglobin': np.random.normal(13.5, 2),
            'wbc': np.random.normal(7.5, 2.5),
            'sodium': np.random.normal(140, 3),
            'potassium': np.random.normal(4.0, 0.5),
            'bun': max(5, np.random.normal(15 + age_factor * 10, 5))
        }
        
        # Round values
        labs = {k: round(v, 2) for k, v in labs.items()}
        
        lab_data.append({
            'patient_id': patient['patient_id'],
            **labs
        })
    
    return pd.DataFrame(lab_data)


def generate_vital_signs(patients_df):
    """Generate vital signs"""
    vitals_data = []
    
    for _, patient in patients_df.iterrows():
        age_factor = patient['age'] / 100
        bmi_factor = patient['bmi'] / 30
        
        vitals = {
            'bp_systolic': max(90, np.random.normal(120 + age_factor * 20 + bmi_factor * 10, 15)),
            'bp_diastolic': max(60, np.random.normal(80 + age_factor * 5 + bmi_factor * 5, 10)),
            'heart_rate': np.random.normal(75, 12),
            'respiratory_rate': np.random.normal(16, 3),
            'temperature': np.random.normal(98.6, 0.5),
            'oxygen_saturation': max(85, np.random.normal(97, 2))
        }
        
        # Round values
        vitals = {k: round(v, 1) for k, v in vitals.items()}
        
        vitals_data.append({
            'patient_id': patient['patient_id'],
            **vitals
        })
    
    return pd.DataFrame(vitals_data)


def generate_admission_history(patients_df):
    """Generate admission history"""
    admission_data = []
    
    for _, patient in patients_df.iterrows():
        # Older patients and higher BMI = more admissions
        admission_prob = (patient['age'] / 100) * 0.5 + (patient['bmi'] / 40) * 0.3
        
        admissions_last_year = np.random.poisson(admission_prob * 3)
        
        # Current admission
        los = max(1, int(np.random.exponential(5)))  # Length of stay
        icu_stay = random.random() < (0.1 + admission_prob * 0.2)
        
        admission_data.append({
            'patient_id': patient['patient_id'],
            'los': los,
            'icu_stay': icu_stay,
            'admissions_last_year': admissions_last_year,
            'days_since_last_admission': random.randint(30, 365) if admissions_last_year > 0 else None
        })
    
    return pd.DataFrame(admission_data)


def generate_clinical_notes(patients_df, diagnoses_df):
    """Generate synthetic clinical notes"""
    notes_data = []
    
    templates = [
        "Patient presents with {symptoms}. History of {conditions}. Current medications include {meds}. Physical exam reveals {findings}.",
        "{age_gender} with history of {conditions} admitted for {chief_complaint}. Patient reports {symptoms}. Vital signs stable. Plan: {plan}.",
        "Chief complaint: {chief_complaint}. Patient has known {conditions}. Currently on {meds}. Assessment: {assessment}."
    ]
    
    symptoms_map = {
        'diabetes': ['polyuria', 'polydipsia', 'fatigue'],
        'hypertension': ['headache', 'dizziness'],
        'heart_failure': ['shortness of breath', 'edema', 'fatigue'],
        'copd': ['dyspnea', 'cough', 'wheezing'],
        'ckd': ['fatigue', 'decreased urine output'],
    }
    
    for _, patient in patients_df.iterrows():
        patient_diagnoses = diagnoses_df[diagnoses_df['patient_id'] == patient['patient_id']]['diagnoses'].iloc[0]
        
        # Determine conditions
        conditions = []
        symptoms = []
        for diagnosis in patient_diagnoses:
            for condition, codes in ICD10_CODES.items():
                if diagnosis in codes and condition not in conditions:
                    conditions.append(condition)
                    symptoms.extend(random.sample(
                symptoms_map.get(condition, ['general malaise']), 
                k=min(random.randint(1, 2), len(symptoms_map.get(condition, ['general malaise'])))
            ))
        
        age_gender = f"{patient['age']}yo {patient['gender']}"
        chief_complaint = random.choice(symptoms) if symptoms else "routine follow-up"
        
        note = random.choice(templates).format(
            age_gender=age_gender,
            symptoms=', '.join(symptoms[:3]),
            conditions=', '.join(conditions[:3]),
            meds="multiple medications",
            findings="unremarkable",
            chief_complaint=chief_complaint,
            assessment="stable",
            plan="continue current management"
        )
        
        notes_data.append({
            'patient_id': patient['patient_id'],
            'clinical_notes': note
        })
    
    return pd.DataFrame(notes_data)


def generate_outcomes(patients_df, diagnoses_df, medications_df, admission_df):
    """Generate outcome labels (readmission and disease progression)"""
    outcomes_data = []
    
    for _, patient in patients_df.iterrows():
        patient_id = patient['patient_id']
        
        # Get patient data
        n_diagnoses = diagnoses_df[diagnoses_df['patient_id'] == patient_id]['n_diagnoses'].iloc[0]
        n_meds = medications_df[medications_df['patient_id'] == patient_id]['n_medications'].iloc[0]
        admissions = admission_df[admission_df['patient_id'] == patient_id]['admissions_last_year'].iloc[0]
        icu_stay = admission_df[admission_df['patient_id'] == patient_id]['icu_stay'].iloc[0]
        los = admission_df[admission_df['patient_id'] == patient_id]['los'].iloc[0]
        
        # Calculate readmission probability
        readmission_prob = 0.1  # Base rate
        readmission_prob += (patient['age'] / 100) * 0.3
        readmission_prob += (n_diagnoses / 10) * 0.2
        readmission_prob += (admissions / 5) * 0.2
        readmission_prob += 0.15 if icu_stay else 0
        readmission_prob += (los / 20) * 0.1
        readmission_prob = min(0.9, readmission_prob)
        
        readmission_30day = random.random() < readmission_prob
        
        # Calculate disease progression risk
        progression_score = 0
        progression_score += (patient['age'] / 100) * 30
        progression_score += (n_diagnoses / 10) * 25
        progression_score += (patient['bmi'] / 40) * 15
        progression_score += (n_meds / 10) * 10
        progression_score += 20 if icu_stay else 0
        
        if progression_score < 30:
            disease_progression = 'low'
        elif progression_score < 60:
            disease_progression = 'medium'
        else:
            disease_progression = 'high'
        
        outcomes_data.append({
            'patient_id': patient_id,
            'readmission_30day': int(readmission_30day),
            'readmission_probability': round(readmission_prob, 3),
            'disease_progression': disease_progression,
            'progression_score': round(progression_score, 2)
        })
    
    return pd.DataFrame(outcomes_data)


def main():
    """Generate complete synthetic dataset"""
    print("Generating synthetic patient data...")
    
    n_patients = 500000  # Generate 500,000 patients for ~4GB dataset
    
    # Generate data
    print(f"Creating {n_patients} patients...")
    patients_df = generate_patient_demographics(n_patients)
    
    print("Generating diagnoses...")
    diagnoses_df = generate_diagnoses(patients_df)
    
    print("Generating medications...")
    medications_df = generate_medications(patients_df, diagnoses_df)
    
    print("Generating lab values...")
    lab_df = generate_lab_values(patients_df)
    
    print("Generating vital signs...")
    vitals_df = generate_vital_signs(patients_df)
    
    print("Generating admission history...")
    admission_df = generate_admission_history(patients_df)
    
    print("Generating clinical notes...")
    notes_df = generate_clinical_notes(patients_df, diagnoses_df)
    
    print("Generating outcomes...")
    outcomes_df = generate_outcomes(patients_df, diagnoses_df, medications_df, admission_df)
    
    # Merge all data
    print("Merging datasets...")
    full_df = patients_df.merge(diagnoses_df, on='patient_id')
    full_df = full_df.merge(medications_df, on='patient_id')
    full_df = full_df.merge(lab_df, on='patient_id')
    full_df = full_df.merge(vitals_df, on='patient_id')
    full_df = full_df.merge(admission_df, on='patient_id')
    full_df = full_df.merge(notes_df, on='patient_id')
    full_df = full_df.merge(outcomes_df, on='patient_id')
    
    # Save to CSV
    output_path = Path('datasets/synthetic/training_data.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Saving to {output_path}...")
    full_df.to_csv(output_path, index=False)
    
    # Print statistics
    print("\n=== Dataset Statistics ===")
    print(f"Total patients: {len(full_df)}")
    print(f"Readmission rate: {full_df['readmission_30day'].mean():.1%}")
    print(f"Disease progression distribution:")
    print(full_df['disease_progression'].value_counts(normalize=True))
    print(f"\nAverage age: {full_df['age'].mean():.1f}")
    print(f"Average BMI: {full_df['bmi'].mean():.1f}")
    print(f"Average diagnoses per patient: {full_df['n_diagnoses'].mean():.1f}")
    print(f"Average medications per patient: {full_df['n_medications'].mean():.1f}")
    
    print(f"\nData saved successfully to {output_path}")
    print("Ready for model training!")


if __name__ == "__main__":
    main()

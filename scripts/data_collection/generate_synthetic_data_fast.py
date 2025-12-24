"""
FAST Synthetic Patient Data Generator - Optimized for Large Datasets

Uses multiprocessing and vectorized operations for 10x faster generation
"""

import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count
import random
from pathlib import Path
from datetime import datetime

# Set seeds
np.random.seed(42)
random.seed(42)

# ICD-10 codes
ICD10_CODES = {
    'diabetes': ['E11.9', 'E11.65', 'E11.22'],
    'hypertension': ['I10', 'I11.9'],
    'heart_failure': ['I50.9', 'I50.1'],
    'copd': ['J44.9', 'J44.1'],
    'ckd': ['N18.3', 'N18.4'],
}

MEDICATIONS = {
    'diabetes': ['metformin', 'insulin glargine'],
    'hypertension': ['lisinopril', 'amlodipine'],
    'heart_failure': ['furosemide', 'carvedilol'],
}


def generate_batch(batch_id, batch_size):
    """Generate a batch of patients"""
    print(f"Processing batch {batch_id}...")
    
    start_id = batch_id * batch_size
    
    # Vectorized generation
    age_groups = np.random.choice([0, 1, 2], batch_size, p=[0.2, 0.3, 0.5])
    ages = np.where(age_groups == 0, np.random.randint(18, 45, batch_size),
                   np.where(age_groups == 1, np.random.randint(45, 65, batch_size),
                           np.random.randint(65, 95, batch_size)))
    
    genders = np.random.choice(['M', 'F'], batch_size)
    bmis = np.clip(np.random.normal(28, 6, batch_size), 15, 50)
    
    # Generate diagnoses (simplified)
    n_diagnoses = np.minimum(1 + (ages // 20).astype(int), 8)
    
    # Generate outcomes
    readmission_probs = 0.1 + (ages / 100) * 0.3 + (n_diagnoses / 10) * 0.2
    readmissions = (np.random.random(batch_size) < readmission_probs).astype(int)
    
    progression_scores = (ages / 100) * 30 + (n_diagnoses / 10) * 25 + (bmis / 40) * 15
    progressions = np.where(progression_scores < 30, 'low',
                           np.where(progression_scores < 60, 'medium', 'high'))
    
    # Create DataFrame
    data = {
        'patient_id': [f'PAT{start_id + i:06d}' for i in range(batch_size)],
        'age': ages,
        'gender': genders,
        'bmi': np.round(bmis, 1),
        'diagnoses': [str(['I50.9', 'E11.9'][:int(n)]) for n in n_diagnoses],
        'primary_diagnosis': ['I50.9'] * batch_size,
        'medications': [str(['metformin', 'lisinopril'])] * batch_size,
        'n_diagnoses': n_diagnoses,
        'n_medications': np.random.randint(1, 8, batch_size),
        'polypharmacy': (np.random.randint(1, 8, batch_size) > 5).astype(int),
        
        # Labs
        'glucose': np.maximum(70, np.random.normal(100 + ages/100*50, 30, batch_size)),
        'creatinine': np.maximum(0.5, np.random.normal(0.9 + ages/100*0.5, 0.3, batch_size)),
        'hemoglobin': np.random.normal(13.5, 2, batch_size),
        'wbc': np.random.normal(7.5, 2.5, batch_size),
        'sodium': np.random.normal(140, 3, batch_size),
        'potassium': np.random.normal(4.0, 0.5, batch_size),
        'bun': np.maximum(5, np.random.normal(15 + ages/100*10, 5, batch_size)),
        
        # Vitals
        'bp_systolic': np.maximum(90, np.random.normal(120 + ages/100*20, 15, batch_size)),
        'bp_diastolic': np.maximum(60, np.random.normal(80 + ages/100*5, 10, batch_size)),
        'heart_rate': np.random.normal(75, 12, batch_size),
        'respiratory_rate': np.random.normal(16, 3, batch_size),
        'temperature': np.random.normal(98.6, 0.5, batch_size),
        'oxygen_saturation': np.maximum(85, np.random.normal(97, 2, batch_size)),
        
        # Admission
        'los': np.maximum(1, np.random.exponential(5, batch_size).astype(int)),
        'icu_stay': (np.random.random(batch_size) < 0.15).astype(int),
        'admissions_last_year': np.random.poisson(1.5, batch_size),
        'days_since_last_admission': np.random.randint(30, 365, batch_size),
        
        # Clinical notes (simplified)
        'clinical_notes': [f"Patient {age}yo {gender} with multiple comorbidities" 
                          for age, gender in zip(ages, genders)],
        
        # Outcomes
        'readmission_30day': readmissions,
        'readmission_probability': np.round(readmission_probs, 3),
        'disease_progression': progressions,
        'progression_score': np.round(progression_scores, 2)
    }
    
    return pd.DataFrame(data)


def main():
    """Generate large dataset using parallel processing"""
    print("="*60)
    print("FAST Synthetic Data Generator")
    print("="*60)
    
    # Configuration
    total_patients = 500000
    batch_size = 10000  # Process 10k at a time
    n_batches = total_patients // batch_size
    n_workers = min(cpu_count(), 8)  # Use up to 8 cores
    
    print(f"\nGenerating {total_patients:,} patients")
    print(f"Batch size: {batch_size:,}")
    print(f"Number of batches: {n_batches}")
    print(f"Using {n_workers} CPU cores")
    print(f"Estimated time: 2-3 minutes\n")
    
    start_time = datetime.now()
    
    # Generate in parallel
    with Pool(n_workers) as pool:
        batch_args = [(i, batch_size) for i in range(n_batches)]
        results = pool.starmap(generate_batch, batch_args)
    
    # Combine all batches
    print("\nCombining batches...")
    df = pd.concat(results, ignore_index=True)
    
    # Save
    output_path = Path('datasets/synthetic/training_data.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Saving to {output_path}...")
    df.to_csv(output_path, index=False)
    
    # Statistics
    elapsed = (datetime.now() - start_time).total_seconds()
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    
    print("\n" + "="*60)
    print("Generation Complete!")
    print("="*60)
    print(f"Total patients: {len(df):,}")
    print(f"File size: {file_size_mb:.1f} MB")
    print(f"Time taken: {elapsed:.1f} seconds")
    print(f"Speed: {len(df)/elapsed:.0f} patients/second")
    print(f"\nReadmission rate: {df['readmission_30day'].mean():.1%}")
    print(f"Disease progression distribution:")
    print(df['disease_progression'].value_counts(normalize=True))
    print(f"\nData saved to: {output_path}")


if __name__ == "__main__":
    main()

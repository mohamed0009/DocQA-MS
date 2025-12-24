"""Show patient data information"""
import pandas as pd

# Load dataset
df = pd.read_csv('datasets/synthetic/training_data.csv', nrows=3)

print("="*70)
print("PATIENT DATASET INFORMATION")
print("="*70)
print(f"\nTotal columns: {len(df.columns)}")
print(f"\n--- ALL PATIENT FIELDS ---\n")

# Group fields by category
demographics = ['patient_id', 'age', 'gender', 'bmi']
diagnoses = ['diagnoses', 'primary_diagnosis', 'n_diagnoses']
medications = ['medications', 'n_medications', 'polypharmacy']
labs = ['glucose', 'creatinine', 'hemoglobin', 'wbc', 'sodium', 'potassium', 'bun']
vitals = ['bp_systolic', 'bp_diastolic', 'heart_rate', 'respiratory_rate', 'temperature', 'oxygen_saturation']
admission = ['los', 'icu_stay', 'admissions_last_year', 'days_since_last_admission']
clinical = ['clinical_notes']
outcomes = ['readmission_30day', 'readmission_probability', 'disease_progression', 'progression_score']

print("📋 DEMOGRAPHICS (4 fields):")
for col in demographics:
    print(f"  - {col}")

print("\n🏥 DIAGNOSES (3 fields):")
for col in diagnoses:
    print(f"  - {col}")

print("\n💊 MEDICATIONS (3 fields):")
for col in medications:
    print(f"  - {col}")

print("\n🧪 LABORATORY VALUES (7 fields):")
for col in labs:
    print(f"  - {col}")

print("\n❤️ VITAL SIGNS (6 fields):")
for col in vitals:
    print(f"  - {col}")

print("\n🏨 ADMISSION HISTORY (4 fields):")
for col in admission:
    print(f"  - {col}")

print("\n📝 CLINICAL NOTES (1 field):")
for col in clinical:
    print(f"  - {col}")

print("\n🎯 OUTCOMES/TARGETS (4 fields):")
for col in outcomes:
    print(f"  - {col}")

print(f"\n{'='*70}")
print("SAMPLE PATIENT RECORDS")
print("="*70)
print("\nFirst 3 patients:\n")
print(df[['patient_id', 'age', 'gender', 'bmi', 'n_diagnoses', 'n_medications', 
         'readmission_30day', 'disease_progression']].to_string(index=False))

print(f"\n{'='*70}")
print("DETAILED VIEW - PATIENT 1")
print("="*70)
patient1 = df.iloc[0]
print(f"\n👤 Patient ID: {patient1['patient_id']}")
print(f"   Age: {patient1['age']} years")
print(f"   Gender: {patient1['gender']}")
print(f"   BMI: {patient1['bmi']}")
print(f"\n🏥 Diagnoses: {patient1['diagnoses']}")
print(f"   Primary: {patient1['primary_diagnosis']}")
print(f"   Count: {patient1['n_diagnoses']}")
print(f"\n💊 Medications: {patient1['medications']}")
print(f"   Count: {patient1['n_medications']}")
print(f"   Polypharmacy: {'Yes' if patient1['polypharmacy'] else 'No'}")
print(f"\n🧪 Lab Values:")
print(f"   Glucose: {patient1['glucose']:.1f} mg/dL")
print(f"   Creatinine: {patient1['creatinine']:.2f} mg/dL")
print(f"   Hemoglobin: {patient1['hemoglobin']:.1f} g/dL")
print(f"\n❤️ Vital Signs:")
print(f"   BP: {patient1['bp_systolic']:.0f}/{patient1['bp_diastolic']:.0f} mmHg")
print(f"   Heart Rate: {patient1['heart_rate']:.0f} bpm")
print(f"   O2 Sat: {patient1['oxygen_saturation']:.1f}%")
print(f"\n🏨 Admission:")
print(f"   Length of Stay: {patient1['los']} days")
print(f"   ICU Stay: {'Yes' if patient1['icu_stay'] else 'No'}")
print(f"   Admissions Last Year: {patient1['admissions_last_year']}")
print(f"\n🎯 Outcomes:")
print(f"   30-Day Readmission: {'YES' if patient1['readmission_30day'] else 'NO'}")
print(f"   Readmission Risk: {patient1['readmission_probability']:.1%}")
print(f"   Disease Progression: {patient1['disease_progression'].upper()}")
print(f"   Progression Score: {patient1['progression_score']:.1f}")
print(f"\n📝 Clinical Notes:")
print(f"   {patient1['clinical_notes']}")
print("\n" + "="*70)

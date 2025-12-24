"""
Feature Engineering Module

Extracts and transforms patient data into features for XGBoost models
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from typing import Dict, List, Any, Optional
import structlog

from ..config import settings
from ..schemas.prediction import PatientFeatures

logger = structlog.get_logger()


class FeatureEngineer:
    """Feature engineering for patient data"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=settings.TFIDF_MAX_FEATURES,
            min_df=1,  # Changed from 2 to 1 to work with small batches
            max_df=0.95,  # Increased from 0.8 to avoid conflicts
            stop_words='english'
        )
        self.label_encoders = {}
        self.feature_names = []
        self.is_fitted = False
        
    def extract_demographic_features(self, patient: PatientFeatures) -> Dict[str, float]:
        """Extract demographic features"""
        features = {
            'age': float(patient.age),
            'age_squared': float(patient.age ** 2),
            'age_binned_young': 1.0 if patient.age < 45 else 0.0,
            'age_binned_middle': 1.0 if 45 <= patient.age < 65 else 0.0,
            'age_binned_elderly': 1.0 if patient.age >= 65 else 0.0,
            'gender_M': 1.0 if patient.gender == 'M' else 0.0,
            'gender_F': 1.0 if patient.gender == 'F' else 0.0,
        }
        
        # BMI features
        if patient.bmi:
            features['bmi'] = float(patient.bmi)
            features['bmi_underweight'] = 1.0 if patient.bmi < 18.5 else 0.0
            features['bmi_normal'] = 1.0 if 18.5 <= patient.bmi < 25 else 0.0
            features['bmi_overweight'] = 1.0 if 25 <= patient.bmi < 30 else 0.0
            features['bmi_obese'] = 1.0 if patient.bmi >= 30 else 0.0
        else:
            features['bmi'] = 25.0  # Default
            features['bmi_underweight'] = 0.0
            features['bmi_normal'] = 1.0
            features['bmi_overweight'] = 0.0
            features['bmi_obese'] = 0.0
            
        return features
    
    def extract_diagnosis_features(self, patient: PatientFeatures) -> Dict[str, float]:
        """Extract diagnosis-related features"""
        features = {
            'n_diagnoses': float(len(patient.diagnoses)),
            'has_primary_diagnosis': 1.0 if patient.primary_diagnosis else 0.0,
        }
        
        # ICD-10 category counts
        icd_categories = {
            'diabetes': ['E11', 'E10'],
            'hypertension': ['I10', 'I11', 'I12'],
            'heart_failure': ['I50'],
            'copd': ['J44'],
            'ckd': ['N18'],
            'cad': ['I25'],
            'stroke': ['I63', 'I64', 'I67'],
            'pneumonia': ['J18', 'J15', 'J13']
        }
        
        for category, prefixes in icd_categories.items():
            count = sum(1 for diag in patient.diagnoses if any(diag.startswith(p) for p in prefixes))
            features[f'has_{category}'] = 1.0 if count > 0 else 0.0
            features[f'count_{category}'] = float(count)
        
        # Charlson Comorbidity Index (simplified)
        charlson_score = 0
        if features['has_heart_failure'] > 0:
            charlson_score += 1
        if features['has_diabetes'] > 0:
            charlson_score += 1
        if features['has_copd'] > 0:
            charlson_score += 1
        if features['has_ckd'] > 0:
            charlson_score += 2
        if features['has_stroke'] > 0:
            charlson_score += 1
            
        features['charlson_index'] = float(charlson_score)
        
        return features
    
    def extract_medication_features(self, patient: PatientFeatures) -> Dict[str, float]:
        """Extract medication-related features"""
        features = {
            'n_medications': float(len(patient.medications)),
            'polypharmacy': 1.0 if len(patient.medications) > 5 else 0.0,
        }
        
        # High-risk medication flags
        high_risk_meds = {
            'anticoagulant': ['warfarin', 'apixaban', 'rivaroxaban', 'dabigatran'],
            'opioid': ['oxycodone', 'hydrocodone', 'morphine', 'fentanyl'],
            'insulin': ['insulin'],
            'diuretic': ['furosemide', 'hydrochlorothiazide', 'spironolactone'],
            'beta_blocker': ['metoprolol', 'carvedilol', 'atenolol'],
            'ace_inhibitor': ['lisinopril', 'enalapril', 'ramipril'],
            'statin': ['atorvastatin', 'simvastatin', 'rosuvastatin']
        }
        
        for category, med_list in high_risk_meds.items():
            has_med = any(any(med.lower() in patient_med.lower() for med in med_list) 
                         for patient_med in patient.medications)
            features[f'on_{category}'] = 1.0 if has_med else 0.0
        
        return features
    
    def extract_lab_features(self, patient: PatientFeatures) -> Dict[str, float]:
        """Extract laboratory value features"""
        features = {}
        
        # Expected lab values with normal ranges
        lab_ranges = {
            'glucose': (70, 100),
            'creatinine': (0.7, 1.3),
            'hemoglobin': (12, 16),
            'wbc': (4, 11),
            'sodium': (136, 145),
            'potassium': (3.5, 5.0),
            'bun': (7, 20)
        }
        
        for lab, (low, high) in lab_ranges.items():
            value = patient.lab_values.get(lab)
            if value is not None:
                features[f'lab_{lab}'] = float(value)
                features[f'lab_{lab}_abnormal'] = 1.0 if (value < low or value > high) else 0.0
                features[f'lab_{lab}_high'] = 1.0 if value > high else 0.0
                features[f'lab_{lab}_low'] = 1.0 if value < low else 0.0
            else:
                # Impute with median
                median = (low + high) / 2
                features[f'lab_{lab}'] = median
                features[f'lab_{lab}_abnormal'] = 0.0
                features[f'lab_{lab}_high'] = 0.0
                features[f'lab_{lab}_low'] = 0.0
        
        return features
    
    def extract_vital_features(self, patient: PatientFeatures) -> Dict[str, float]:
        """Extract vital signs features"""
        features = {}
        
        vital_ranges = {
            'bp_systolic': (90, 120),
            'bp_diastolic': (60, 80),
            'heart_rate': (60, 100),
            'respiratory_rate': (12, 20),
            'temperature': (97, 99),
            'oxygen_saturation': (95, 100)
        }
        
        for vital, (low, high) in vital_ranges.items():
            value = patient.vital_signs.get(vital)
            if value is not None:
                features[f'vital_{vital}'] = float(value)
                features[f'vital_{vital}_abnormal'] = 1.0 if (value < low or value > high) else 0.0
            else:
                median = (low + high) / 2
                features[f'vital_{vital}'] = median
                features[f'vital_{vital}_abnormal'] = 0.0
        
        # Derived features
        if 'bp_systolic' in patient.vital_signs and 'bp_diastolic' in patient.vital_signs:
            features['pulse_pressure'] = float(patient.vital_signs['bp_systolic'] - patient.vital_signs['bp_diastolic'])
        else:
            features['pulse_pressure'] = 40.0
        
        return features
    
    def extract_admission_features(self, patient: PatientFeatures) -> Dict[str, float]:
        """Extract admission history features"""
        features = {}
        
        admission_hist = patient.admission_history
        
        features['los'] = float(admission_hist.get('los', 3))
        features['los_long'] = 1.0 if admission_hist.get('los', 0) > 7 else 0.0
        features['icu_stay'] = 1.0 if admission_hist.get('icu_stay', False) else 0.0
        features['admissions_last_year'] = float(admission_hist.get('admissions_last_year', 0))
        features['frequent_admitter'] = 1.0 if admission_hist.get('admissions_last_year', 0) > 2 else 0.0
        
        days_since = admission_hist.get('days_since_last_admission')
        if days_since is not None:
            features['days_since_last_admission'] = float(days_since)
            features['recent_admission'] = 1.0 if days_since < 90 else 0.0
        else:
            features['days_since_last_admission'] = 365.0
            features['recent_admission'] = 0.0
        
        return features
    
    def extract_text_features(self, patient: PatientFeatures, fit: bool = False) -> Dict[str, float]:
        """Extract TF-IDF features from clinical notes"""
        features = {}
        
        if patient.clinical_notes:
            text = patient.clinical_notes[:settings.MAX_TEXT_LENGTH]
            
            if fit:
                # Fit vectorizer (only during training)
                tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
            else:
                # Transform only
                if self.is_fitted:
                    tfidf_matrix = self.tfidf_vectorizer.transform([text])
                else:
                    # If not fitted, return zeros
                    for i in range(settings.TFIDF_MAX_FEATURES):
                        features[f'tfidf_{i}'] = 0.0
                    return features
            
            # Convert to features
            tfidf_array = tfidf_matrix.toarray()[0]
            for i, value in enumerate(tfidf_array):
                features[f'tfidf_{i}'] = float(value)
            
            # Text statistics
            features['note_length'] = float(len(text))
            features['note_word_count'] = float(len(text.split()))
        else:
            # No notes - return zeros
            for i in range(settings.TFIDF_MAX_FEATURES):
                features[f'tfidf_{i}'] = 0.0
            features['note_length'] = 0.0
            features['note_word_count'] = 0.0
        
        return features
    
    def extract_features(self, patient: PatientFeatures, fit: bool = False) -> np.ndarray:
        """Extract all features from patient data"""
        all_features = {}
        
        # Extract all feature groups
        all_features.update(self.extract_demographic_features(patient))
        all_features.update(self.extract_diagnosis_features(patient))
        all_features.update(self.extract_medication_features(patient))
        all_features.update(self.extract_lab_features(patient))
        all_features.update(self.extract_vital_features(patient))
        all_features.update(self.extract_admission_features(patient))
        all_features.update(self.extract_text_features(patient, fit=fit))
        
        # Store feature names on first extraction
        if not self.feature_names:
            self.feature_names = sorted(all_features.keys())
        
        # Convert to array in consistent order
        feature_array = np.array([all_features[name] for name in self.feature_names])
        
        return feature_array.reshape(1, -1)
    
    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        """Fit feature engineer on training data and transform"""
        logger.info("Fitting feature engineer on training data")
        
        # This would be called during training with a DataFrame
        # For now, we'll implement a simplified version
        self.is_fitted = True
        return None
    
    def transform(self, patient: PatientFeatures) -> np.ndarray:
        """Transform patient data to features"""
        return self.extract_features(patient, fit=False)
    
    def save(self, filepath: str):
        """Save feature engineer to disk"""
        joblib.dump(self, filepath)
        logger.info("Feature engineer saved", filepath=filepath)
    
    @staticmethod
    def load(filepath: str) -> 'FeatureEngineer':
        """Load feature engineer from disk"""
        engineer = joblib.load(filepath)
        logger.info("Feature engineer loaded", filepath=filepath)
        return engineer

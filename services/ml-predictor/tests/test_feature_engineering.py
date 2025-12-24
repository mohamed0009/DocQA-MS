"""
Unit tests for feature engineering
"""

import pytest
import numpy as np
from app.ml.feature_engineering import FeatureEngineer
from app.schemas.prediction import PatientFeatures


@pytest.fixture
def sample_patient():
    """Create sample patient for testing"""
    return PatientFeatures(
        patient_id="TEST001",
        age=68,
        gender="M",
        bmi=28.5,
        diagnoses=["I50.9", "E11.9", "I10"],
        primary_diagnosis="I50.9",
        medications=["metformin", "lisinopril", "atorvastatin"],
        lab_values={
            "glucose": 145,
            "creatinine": 1.2,
            "hemoglobin": 12.5
        },
        vital_signs={
            "bp_systolic": 140,
            "bp_diastolic": 90,
            "heart_rate": 75
        },
        admission_history={
            "los": 5,
            "icu_stay": True,
            "admissions_last_year": 2
        },
        clinical_notes="Patient presents with shortness of breath and fatigue."
    )


@pytest.fixture
def feature_engineer():
    """Create feature engineer instance"""
    engineer = FeatureEngineer()
    engineer.is_fitted = True
    return engineer


def test_demographic_features(feature_engineer, sample_patient):
    """Test demographic feature extraction"""
    features = feature_engineer.extract_demographic_features(sample_patient)
    
    assert features['age'] == 68.0
    assert features['gender_M'] == 1.0
    assert features['gender_F'] == 0.0
    assert features['bmi'] == 28.5
    assert features['age_binned_elderly'] == 1.0
    assert features['bmi_overweight'] == 1.0


def test_diagnosis_features(feature_engineer, sample_patient):
    """Test diagnosis feature extraction"""
    features = feature_engineer.extract_diagnosis_features(sample_patient)
    
    assert features['n_diagnoses'] == 3.0
    assert features['has_heart_failure'] == 1.0
    assert features['has_diabetes'] == 1.0
    assert features['has_hypertension'] == 1.0
    assert features['charlson_index'] > 0


def test_medication_features(feature_engineer, sample_patient):
    """Test medication feature extraction"""
    features = feature_engineer.extract_medication_features(sample_patient)
    
    assert features['n_medications'] == 3.0
    assert features['polypharmacy'] == 0.0  # < 5 medications
    assert features['on_statin'] == 1.0


def test_lab_features(feature_engineer, sample_patient):
    """Test lab value feature extraction"""
    features = feature_engineer.extract_lab_features(sample_patient)
    
    assert 'lab_glucose' in features
    assert features['lab_glucose'] == 145.0
    assert features['lab_glucose_high'] == 1.0  # > 100
    assert 'lab_creatinine' in features


def test_vital_features(feature_engineer, sample_patient):
    """Test vital signs feature extraction"""
    features = feature_engineer.extract_vital_features(sample_patient)
    
    assert 'vital_bp_systolic' in features
    assert features['vital_bp_systolic'] == 140.0
    assert features['vital_bp_systolic_abnormal'] == 1.0  # > 120
    assert 'pulse_pressure' in features


def test_admission_features(feature_engineer, sample_patient):
    """Test admission history feature extraction"""
    features = feature_engineer.extract_admission_features(sample_patient)
    
    assert features['los'] == 5.0
    assert features['icu_stay'] == 1.0
    assert features['admissions_last_year'] == 2.0
    assert features['frequent_admitter'] == 0.0  # <= 2


def test_missing_values_handling(feature_engineer):
    """Test handling of missing values"""
    patient = PatientFeatures(
        patient_id="TEST002",
        age=50,
        gender="F",
        diagnoses=[],
        medications=[],
        lab_values={},
        vital_signs={},
        admission_history={}
    )
    
    features = feature_engineer.extract_demographic_features(patient)
    assert 'bmi' in features  # Should have default value
    
    lab_features = feature_engineer.extract_lab_features(patient)
    assert all('lab_' in k for k in lab_features.keys())


def test_feature_extraction_shape(feature_engineer, sample_patient):
    """Test that feature extraction returns correct shape"""
    features = feature_engineer.extract_features(sample_patient, fit=False)
    
    assert isinstance(features, np.ndarray)
    assert features.ndim == 2
    assert features.shape[0] == 1  # Single patient
    assert features.shape[1] > 100  # Should have 200+ features


def test_feature_names_consistency(feature_engineer, sample_patient):
    """Test that feature names are consistent"""
    features1 = feature_engineer.extract_features(sample_patient, fit=False)
    features2 = feature_engineer.extract_features(sample_patient, fit=False)
    
    assert len(feature_engineer.feature_names) > 0
    assert features1.shape == features2.shape

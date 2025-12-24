"""
Pydantic schemas for prediction API
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class RiskCategory(str, Enum):
    """Risk categorization"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ModelType(str, Enum):
    """Available model types"""
    READMISSION = "readmission"
    PROGRESSION = "progression"


class PatientFeatures(BaseModel):
    """Input features for prediction"""
    patient_id: str = Field(..., description="Unique patient identifier")
    
    # Demographics
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    gender: str = Field(..., description="Patient gender (M/F/O)")
    bmi: Optional[float] = Field(None, ge=10, le=80, description="Body Mass Index")
    
    # Diagnoses
    diagnoses: List[str] = Field(default_factory=list, description="List of ICD-10 codes")
    primary_diagnosis: Optional[str] = Field(None, description="Primary diagnosis ICD-10 code")
    
    # Medications
    medications: List[str] = Field(default_factory=list, description="List of current medications")
    
    # Lab Values
    lab_values: Dict[str, float] = Field(
        default_factory=dict,
        description="Laboratory test results (e.g., {'glucose': 145, 'creatinine': 1.2})"
    )
    
    # Vital Signs
    vital_signs: Dict[str, float] = Field(
        default_factory=dict,
        description="Vital signs (e.g., {'bp_systolic': 140, 'bp_diastolic': 90, 'heart_rate': 75})"
    )
    
    # Admission History
    admission_history: Dict[str, Any] = Field(
        default_factory=dict,
        description="Admission details (e.g., {'los': 5, 'icu_stay': true, 'admissions_last_year': 2})"
    )
    
    # Clinical Notes
    clinical_notes: Optional[str] = Field(None, max_length=10000, description="Clinical notes text")
    
    class Config:
        schema_extra = {
            "example": {
                "patient_id": "PAT001",
                "age": 68,
                "gender": "M",
                "bmi": 28.5,
                "diagnoses": ["I50.9", "E11.9", "I10"],
                "primary_diagnosis": "I50.9",
                "medications": ["metformin", "lisinopril", "atorvastatin"],
                "lab_values": {
                    "glucose": 145,
                    "creatinine": 1.2,
                    "hemoglobin": 12.5
                },
                "vital_signs": {
                    "bp_systolic": 140,
                    "bp_diastolic": 90,
                    "heart_rate": 75,
                    "temperature": 98.6
                },
                "admission_history": {
                    "los": 5,
                    "icu_stay": True,
                    "admissions_last_year": 2
                },
                "clinical_notes": "Patient presents with shortness of breath and fatigue..."
            }
        }


class PredictionRequest(BaseModel):
    """Request for prediction"""
    patient_features: PatientFeatures
    model_type: ModelType = Field(ModelType.READMISSION, description="Type of prediction to make")
    explain: bool = Field(True, description="Include SHAP explanations")
    
    class Config:
        use_enum_values = True


class RiskFactor(BaseModel):
    """Individual risk factor contribution"""
    feature: str = Field(..., description="Feature name")
    value: Any = Field(..., description="Feature value")
    contribution: float = Field(..., description="SHAP contribution to prediction")
    direction: str = Field(..., description="Increases or decreases risk")


class PredictionResponse(BaseModel):
    """Prediction response"""
    patient_id: str
    model_type: str
    prediction: float = Field(..., description="Prediction score (probability for binary, class for multiclass)")
    risk_category: RiskCategory
    confidence: float = Field(..., ge=0, le=1, description="Model confidence score")
    
    # Explainability
    top_risk_factors: List[RiskFactor] = Field(default_factory=list, description="Top contributing features")
    shap_base_value: Optional[float] = Field(None, description="SHAP base value (expected value)")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_version: str = Field("1.0.0", description="Model version used")
    
    class Config:
        schema_extra = {
            "example": {
                "patient_id": "PAT001",
                "model_type": "readmission",
                "prediction": 0.72,
                "risk_category": "high",
                "confidence": 0.85,
                "top_risk_factors": [
                    {
                        "feature": "age",
                        "value": 68,
                        "contribution": 0.15,
                        "direction": "increases"
                    },
                    {
                        "feature": "icu_stay",
                        "value": True,
                        "contribution": 0.12,
                        "direction": "increases"
                    }
                ],
                "shap_base_value": 0.35,
                "timestamp": "2025-12-22T12:00:00",
                "model_version": "1.0.0"
            }
        }


class BatchPredictionRequest(BaseModel):
    """Request for batch predictions"""
    patients: List[PatientFeatures]
    model_type: ModelType = Field(ModelType.READMISSION)
    explain: bool = Field(False, description="Include SHAP explanations (slower for batch)")


class BatchPredictionResponse(BaseModel):
    """Batch prediction response"""
    predictions: List[PredictionResponse]
    total_processed: int
    processing_time_ms: int


class ModelInfo(BaseModel):
    """Model information"""
    model_type: str
    model_version: str
    features_count: int
    training_date: Optional[str] = None
    performance_metrics: Dict[str, float] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    models_loaded: bool
    available_models: List[str]

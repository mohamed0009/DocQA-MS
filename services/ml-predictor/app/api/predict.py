"""
Prediction API endpoints
"""

from fastapi import APIRouter, HTTPException, status
import time
from datetime import datetime
import structlog

from ..schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    RiskCategory,
    RiskFactor
)
from ..ml.feature_engineering import FeatureEngineer
from ..ml.model_inference import ModelPredictor
from ..ml.explainability import ModelExplainer
from ..config import settings

logger = structlog.get_logger()
router = APIRouter()


def categorize_risk(prediction: float, model_type: str) -> RiskCategory:
    """Categorize risk based on prediction score"""
    if model_type == "readmission":
        # Binary classification - use thresholds
        if prediction < settings.PREDICTION_THRESHOLD_LOW:
            return RiskCategory.LOW
        elif prediction < settings.PREDICTION_THRESHOLD_HIGH:
            return RiskCategory.MEDIUM
        else:
            return RiskCategory.HIGH
    else:
        # Multi-class - map directly
        if prediction < 0.33:
            return RiskCategory.LOW
        elif prediction < 0.67:
            return RiskCategory.MEDIUM
        else:
            return RiskCategory.HIGH


def calculate_confidence(prediction: float) -> float:
    """Calculate confidence score"""
    # For binary classification, confidence is distance from 0.5
    distance_from_uncertain = abs(prediction - 0.5)
    confidence = 0.5 + distance_from_uncertain
    return min(1.0, confidence)


@router.post("/predict", response_model=PredictionResponse)
async def predict_risk(request: PredictionRequest):
    """
    Predict patient risk using XGBoost models
    
    - **patient_features**: Patient clinical data
    - **model_type**: Type of prediction (readmission/progression)
    - **explain**: Include SHAP explanations
    
    Returns prediction with risk category and optional explanations
    """
    start_time = time.time()
    
    try:
        # Initialize predictor
        predictor = ModelPredictor(model_type=request.model_type)
        
        # Make prediction
        prediction = predictor.predict(request.patient_features)
        
        # Categorize risk
        risk_category = categorize_risk(prediction, request.model_type)
        
        # Calculate confidence
        confidence = calculate_confidence(prediction)
        
        # Generate explanation if requested
        top_risk_factors = []
        shap_base_value = None
        
        if request.explain:
            try:
                # Get feature engineer
                feature_engineer = predictor._feature_engineer
                
                # Extract features
                features = feature_engineer.extract_features(request.patient_features, fit=False)
                
                # Get model
                model = predictor._models.get(request.model_type)
                
                if model and feature_engineer:
                    # Generate explanation
                    explainer = ModelExplainer(model, feature_engineer.feature_names)
                    
                    # Get original feature values for context
                    feature_values = {}
                    
                    explanation = explainer.explain_prediction(features, feature_values)
                    
                    # Format top features
                    for feat in explanation.get('top_features', [])[:10]:
                        contribution = feat['contribution']
                        top_risk_factors.append(RiskFactor(
                            feature=feat['feature'],
                            value=contribution,  # Simplified - would need actual value
                            contribution=abs(contribution),
                            direction="increases" if contribution > 0 else "decreases"
                        ))
                    
                    shap_base_value = explanation.get('base_value')
                    
            except Exception as e:
                logger.error("Explanation generation failed", error=str(e))
                # Continue without explanation
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            "Prediction completed",
            patient_id=request.patient_features.patient_id,
            model_type=request.model_type,
            prediction=prediction,
            risk_category=risk_category.value,
            processing_time_ms=processing_time_ms
        )
        
        return PredictionResponse(
            patient_id=request.patient_features.patient_id,
            model_type=request.model_type,
            prediction=prediction,
            risk_category=risk_category,
            confidence=confidence,
            top_risk_factors=top_risk_factors,
            shap_base_value=shap_base_value,
            timestamp=datetime.utcnow(),
            model_version="1.0.0"
        )
        
    except Exception as e:
        logger.error("Prediction failed", error=str(e), patient_id=request.patient_features.patient_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(request: BatchPredictionRequest):
    """
    Batch prediction for multiple patients
    
    - **patients**: List of patient features
    - **model_type**: Type of prediction
    - **explain**: Include explanations (slower for batch)
    
    Returns list of predictions
    """
    start_time = time.time()
    
    try:
        predictions = []
        
        for patient_features in request.patients:
            # Create individual prediction request
            pred_request = PredictionRequest(
                patient_features=patient_features,
                model_type=request.model_type,
                explain=request.explain
            )
            
            # Get prediction
            pred_response = await predict_risk(pred_request)
            predictions.append(pred_response)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            "Batch prediction completed",
            total_patients=len(predictions),
            processing_time_ms=processing_time_ms
        )
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_processed=len(predictions),
            processing_time_ms=processing_time_ms
        )
        
    except Exception as e:
        logger.error("Batch prediction failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )


@router.get("/models")
async def list_models():
    """
    List available models and their status
    
    Returns information about loaded models
    """
    available_models = ModelPredictor.get_available_models()
    
    return {
        "available_models": available_models,
        "models_loaded": ModelPredictor.are_models_loaded(),
        "model_path": settings.MODEL_PATH
    }

"""
Integration tests for prediction API
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_prediction_request():
    """Sample prediction request"""
    return {
        "patient_features": {
            "patient_id": "TEST001",
            "age": 68,
            "gender": "M",
            "bmi": 28.5,
            "diagnoses": ["I50.9", "E11.9"],
            "primary_diagnosis": "I50.9",
            "medications": ["metformin", "lisinopril"],
            "lab_values": {
                "glucose": 145,
                "creatinine": 1.2
            },
            "vital_signs": {
                "bp_systolic": 140,
                "bp_diastolic": 90
            },
            "admission_history": {
                "los": 5,
                "icu_stay": True,
                "admissions_last_year": 2
            }
        },
        "model_type": "readmission",
        "explain": True
    }


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "service" in data
    assert data["service"] == "ml-predictor"


def test_readiness_check(client):
    """Test readiness endpoint"""
    response = client.get("/api/ready")
    
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data


def test_liveness_check(client):
    """Test liveness endpoint"""
    response = client.get("/api/live")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_prediction_endpoint(client, sample_prediction_request):
    """Test prediction endpoint"""
    response = client.post("/api/predict", json=sample_prediction_request)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "patient_id" in data
    assert "prediction" in data
    assert "risk_category" in data
    assert "confidence" in data
    assert "timestamp" in data
    
    # Check data types
    assert isinstance(data["prediction"], float)
    assert 0 <= data["prediction"] <= 1
    assert data["risk_category"] in ["low", "medium", "high"]
    assert 0 <= data["confidence"] <= 1


def test_prediction_with_explanation(client, sample_prediction_request):
    """Test prediction with SHAP explanation"""
    sample_prediction_request["explain"] = True
    
    response = client.post("/api/predict", json=sample_prediction_request)
    
    assert response.status_code == 200
    data = response.json()
    
    # Should have risk factors when explain=True
    assert "top_risk_factors" in data


def test_prediction_without_explanation(client, sample_prediction_request):
    """Test prediction without explanation"""
    sample_prediction_request["explain"] = False
    
    response = client.post("/api/predict", json=sample_prediction_request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "prediction" in data


def test_progression_model(client, sample_prediction_request):
    """Test disease progression model"""
    sample_prediction_request["model_type"] = "progression"
    
    response = client.post("/api/predict", json=sample_prediction_request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["model_type"] == "progression"


def test_batch_prediction(client, sample_prediction_request):
    """Test batch prediction endpoint"""
    batch_request = {
        "patients": [
            sample_prediction_request["patient_features"],
            sample_prediction_request["patient_features"]
        ],
        "model_type": "readmission",
        "explain": False
    }
    
    response = client.post("/api/predict/batch", json=batch_request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "predictions" in data
    assert len(data["predictions"]) == 2
    assert "total_processed" in data
    assert data["total_processed"] == 2


def test_list_models(client):
    """Test list models endpoint"""
    response = client.get("/api/models")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "available_models" in data
    assert "models_loaded" in data


def test_invalid_patient_data(client):
    """Test with invalid patient data"""
    invalid_request = {
        "patient_features": {
            "patient_id": "TEST001",
            "age": -5,  # Invalid age
            "gender": "M"
        },
        "model_type": "readmission"
    }
    
    response = client.post("/api/predict", json=invalid_request)
    
    assert response.status_code == 422  # Validation error


def test_missing_required_fields(client):
    """Test with missing required fields"""
    incomplete_request = {
        "patient_features": {
            "patient_id": "TEST001"
            # Missing age and gender
        },
        "model_type": "readmission"
    }
    
    response = client.post("/api/predict", json=incomplete_request)
    
    assert response.status_code == 422


def test_risk_categorization(client, sample_prediction_request):
    """Test that risk is properly categorized"""
    response = client.post("/api/predict", json=sample_prediction_request)
    
    assert response.status_code == 200
    data = response.json()
    
    prediction = data["prediction"]
    risk_category = data["risk_category"]
    
    # Verify categorization logic
    if prediction < 0.3:
        assert risk_category == "low"
    elif prediction < 0.7:
        assert risk_category == "medium"
    else:
        assert risk_category == "high"

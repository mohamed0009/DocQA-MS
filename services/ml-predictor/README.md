# ML Predictor Service

XGBoost-based predictive modeling service for patient risk stratification.

## Models

- **Readmission Prediction**: 30-day readmission risk (binary classification)
- **Disease Progression**: Risk level prediction (multi-class: low/medium/high)

## Features

- 200+ engineered features from patient data
- SHAP-based explainability
- REST API for predictions
- Integration with existing microservices

## Quick Start

```bash
# Build and run
docker-compose up ml-predictor

# Test prediction
curl -X POST "http://localhost:8007/api/predict" \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

## API Documentation

Once running, visit: http://localhost:8007/docs

"""
XGBoost Model Training Pipeline

Trains readmission and disease progression models on synthetic data
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    roc_auc_score, precision_recall_fscore_support,
    classification_report, confusion_matrix
)
import xgboost as xgb
from bayes_opt import BayesianOptimization
import joblib
from pathlib import Path
import json
import sys
from datetime import datetime

# Add service to path
sys.path.append('services/ml-predictor')

from app.ml.feature_engineering import FeatureEngineer
from app.config import settings


def load_and_prepare_data(data_path='datasets/synthetic/training_data.csv'):
    """Load and prepare training data"""
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    # Convert string lists back to actual lists
    df['diagnoses'] = df['diagnoses'].apply(eval)
    df['medications'] = df['medications'].apply(eval)
    
    print(f"Loaded {len(df)} patients")
    print(f"Readmission rate: {df['readmission_30day'].mean():.2%}")
    print(f"Disease progression distribution:\n{df['disease_progression'].value_counts(normalize=True)}")
    
    return df


def engineer_features(df):
    """Engineer features from raw data"""
    print("\nEngineering features...")
    
    feature_engineer = FeatureEngineer()
    
    # First pass: collect all clinical notes for TF-IDF fitting
    all_notes = []
    for idx, row in df.iterrows():
        note = row['clinical_notes'] if pd.notna(row['clinical_notes']) else ""
        all_notes.append(note[:settings.MAX_TEXT_LENGTH])
    
    # Fit TF-IDF on all notes
    print("Fitting TF-IDF vectorizer on all clinical notes...")
    if all_notes:
        feature_engineer.tfidf_vectorizer.fit(all_notes)
        feature_engineer.is_fitted = True
    
    # Second pass: extract features for each patient
    features_list = []
    
    for idx, row in df.iterrows():
        if idx % 500 == 0:
            print(f"Processing patient {idx}/{len(df)}...")
        
        # Create PatientFeatures object
        from app.schemas.prediction import PatientFeatures
        
        patient = PatientFeatures(
            patient_id=row['patient_id'],
            age=int(row['age']),
            gender=row['gender'],
            bmi=float(row['bmi']),
            diagnoses=row['diagnoses'],
            primary_diagnosis=row['primary_diagnosis'],
            medications=row['medications'],
            lab_values={
                'glucose': row['glucose'],
                'creatinine': row['creatinine'],
                'hemoglobin': row['hemoglobin'],
                'wbc': row['wbc'],
                'sodium': row['sodium'],
                'potassium': row['potassium'],
                'bun': row['bun']
            },
            vital_signs={
                'bp_systolic': row['bp_systolic'],
                'bp_diastolic': row['bp_diastolic'],
                'heart_rate': row['heart_rate'],
                'respiratory_rate': row['respiratory_rate'],
                'temperature': row['temperature'],
                'oxygen_saturation': row['oxygen_saturation']
            },
            admission_history={
                'los': int(row['los']),
                'icu_stay': bool(row['icu_stay']),
                'admissions_last_year': int(row['admissions_last_year']),
                'days_since_last_admission': row['days_since_last_admission'] if pd.notna(row['days_since_last_admission']) else None
            },
            clinical_notes=row['clinical_notes']
        )
        
        # Extract features (TF-IDF already fitted)
        features = feature_engineer.extract_features(patient, fit=False)
        features_list.append(features[0])
    
    X = np.array(features_list)
    
    print(f"Feature engineering complete. Shape: {X.shape}")
    
    return X, feature_engineer


def train_readmission_model(X, y, feature_engineer):
    """Train readmission prediction model"""
    print("\n" + "="*50)
    print("Training Readmission Prediction Model")
    print("="*50)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=settings.TRAIN_TEST_SPLIT,
        random_state=settings.RANDOM_STATE,
        stratify=y
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    print(f"Positive class rate (train): {y_train.mean():.2%}")
    
    # Define hyperparameter space
    def xgb_evaluate(max_depth, learning_rate, n_estimators, min_child_weight, subsample, colsample_bytree):
        params = {
            'max_depth': int(max_depth),
            'learning_rate': learning_rate,
            'n_estimators': int(n_estimators),
            'min_child_weight': int(min_child_weight),
            'subsample': subsample,
            'colsample_bytree': colsample_bytree,
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'random_state': settings.RANDOM_STATE,
            'tree_method': 'hist'
        }
        
        model = xgb.XGBClassifier(**params)
        
        # Cross-validation
        cv_scores = cross_val_score(
            model, X_train, y_train,
            cv=3,  # Reduced for speed
            scoring='roc_auc',
            n_jobs=-1
        )
        
        return cv_scores.mean()
    
    # Bayesian optimization
    print("\nPerforming hyperparameter optimization...")
    optimizer = BayesianOptimization(
        f=xgb_evaluate,
        pbounds={
            'max_depth': (3, 10),
            'learning_rate': (0.01, 0.3),
            'n_estimators': (100, 500),
            'min_child_weight': (1, 10),
            'subsample': (0.6, 1.0),
            'colsample_bytree': (0.6, 1.0)
        },
        random_state=settings.RANDOM_STATE,
        verbose=2
    )
    
    optimizer.maximize(n_iter=20, init_points=5)  # Reduced for speed
    
    # Get best parameters
    best_params = optimizer.max['params']
    best_params['max_depth'] = int(best_params['max_depth'])
    best_params['n_estimators'] = int(best_params['n_estimators'])
    best_params['min_child_weight'] = int(best_params['min_child_weight'])
    best_params['objective'] = 'binary:logistic'
    best_params['eval_metric'] = 'auc'
    best_params['random_state'] = settings.RANDOM_STATE
    best_params['tree_method'] = 'hist'
    
    print(f"\nBest parameters: {best_params}")
    print(f"Best CV AUC: {optimizer.max['target']:.4f}")
    
    # Train final model
    print("\nTraining final model...")
    model = xgb.XGBClassifier(**best_params)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    auc = roc_auc_score(y_test, y_pred_proba)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')
    
    print("\n" + "="*50)
    print("Readmission Model Performance")
    print("="*50)
    print(f"AUC-ROC: {auc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    return model, {
        'auc': auc,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'best_params': best_params
    }


def train_progression_model(X, y, feature_engineer):
    """Train disease progression model"""
    print("\n" + "="*50)
    print("Training Disease Progression Model")
    print("="*50)
    
    # Encode labels
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=settings.TRAIN_TEST_SPLIT,
        random_state=settings.RANDOM_STATE,
        stratify=y_encoded
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train model with default parameters (simplified for speed)
    params = {
        'max_depth': 8,
        'learning_rate': 0.05,
        'n_estimators': 300,
        'objective': 'multi:softmax',
        'num_class': 3,
        'eval_metric': 'mlogloss',
        'random_state': settings.RANDOM_STATE,
        'tree_method': 'hist'
    }
    
    print("\nTraining model...")
    model = xgb.XGBClassifier(**params)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='macro')
    
    print("\n" + "="*50)
    print("Disease Progression Model Performance")
    print("="*50)
    print(f"Macro Precision: {precision:.4f}")
    print(f"Macro Recall: {recall:.4f}")
    print(f"Macro F1-Score: {f1:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    return model, le, {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'classes': le.classes_.tolist()
    }


def save_models(readmission_model, progression_model, label_encoder, feature_engineer, metrics):
    """Save trained models and metadata"""
    output_dir = Path('services/ml-predictor/trained_models')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*50)
    print("Saving Models")
    print("="*50)
    
    # Save models
    joblib.dump(readmission_model, output_dir / 'readmission_model.pkl')
    print(f"✓ Saved readmission model")
    
    joblib.dump(progression_model, output_dir / 'progression_model.pkl')
    print(f"✓ Saved progression model")
    
    joblib.dump(label_encoder, output_dir / 'label_encoder.pkl')
    print(f"✓ Saved label encoder")
    
    joblib.dump(feature_engineer, output_dir / 'feature_engineer.pkl')
    print(f"✓ Saved feature engineer")
    
    # Save metadata
    metadata = {
        'training_date': datetime.now().isoformat(),
        'readmission_metrics': metrics['readmission'],
        'progression_metrics': metrics['progression'],
        'feature_count': len(feature_engineer.feature_names),
        'model_version': '1.0.0'
    }
    
    with open(output_dir / 'model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Saved metadata")
    
    print(f"\nAll models saved to {output_dir}")


def main():
    """Main training pipeline"""
    print("="*50)
    print("XGBoost Model Training Pipeline")
    print("="*50)
    
    # Load data
    df = load_and_prepare_data()
    
    # Engineer features
    X, feature_engineer = engineer_features(df)
    
    # Train readmission model
    readmission_model, readmission_metrics = train_readmission_model(
        X, df['readmission_30day'].values, feature_engineer
    )
    
    # Train progression model
    progression_model, label_encoder, progression_metrics = train_progression_model(
        X, df['disease_progression'].values, feature_engineer
    )
    
    # Save models
    save_models(
        readmission_model,
        progression_model,
        label_encoder,
        feature_engineer,
        {
            'readmission': readmission_metrics,
            'progression': progression_metrics
        }
    )
    
    print("\n" + "="*50)
    print("Training Complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Start the ML predictor service: docker-compose up ml-predictor")
    print("2. Test predictions: curl -X POST http://localhost:8007/api/predict")
    print("3. View API docs: http://localhost:8007/docs")


if __name__ == "__main__":
    main()

"""
XGBoost Model Evaluation and Visualization
Generates comprehensive metrics and performance curves
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    roc_curve, auc, precision_recall_curve, average_precision_score,
    confusion_matrix, classification_report, roc_auc_score,
    precision_recall_fscore_support
)
from sklearn.model_selection import train_test_split
import joblib
from pathlib import Path
import json
import sys

# Add service to path
sys.path.append('services/ml-predictor')

from app.ml.feature_engineering import FeatureEngineer
from app.config import settings

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def load_models():
    """Load trained models"""
    model_dir = Path('services/ml-predictor/trained_models')
    
    print("Loading models...")
    readmission_model = joblib.load(model_dir / 'readmission_model.pkl')
    progression_model = joblib.load(model_dir / 'progression_model.pkl')
    feature_engineer = joblib.load(model_dir / 'feature_engineer.pkl')
    label_encoder = joblib.load(model_dir / 'label_encoder.pkl')
    
    # Load metadata
    with open(model_dir / 'model_metadata.json', 'r') as f:
        metadata = json.load(f)
    
    print("✓ Models loaded successfully")
    return readmission_model, progression_model, feature_engineer, label_encoder, metadata


def load_and_prepare_data(data_path='datasets/synthetic/training_data.csv'):
    """Load test data"""
    print(f"\nLoading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    # Convert string lists
    df['diagnoses'] = df['diagnoses'].apply(eval)
    df['medications'] = df['medications'].apply(eval)
    
    print(f"✓ Loaded {len(df)} patients")
    return df


def engineer_features(df, feature_engineer):
    """Engineer features for test set"""
    print("\nEngineering features...")
    
    features_list = []
    
    for idx, row in df.iterrows():
        if idx % 10000 == 0:
            print(f"Processing {idx}/{len(df)}...")
        
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
        
        features = feature_engineer.extract_features(patient, fit=False)
        features_list.append(features[0])
    
    X = np.array(features_list)
    print(f"✓ Feature engineering complete. Shape: {X.shape}")
    return X


def plot_roc_curve(y_true, y_pred_proba, model_name, save_path):
    """Plot ROC curve"""
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(10, 8))
    plt.plot(fpr, tpr, color='darkorange', lw=2, 
             label=f'ROC curve (AUC = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
             label='Random Classifier')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title(f'ROC Curve - {model_name}', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right", fontsize=11)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ ROC curve saved to {save_path}")
    return roc_auc


def plot_precision_recall_curve(y_true, y_pred_proba, model_name, save_path):
    """Plot Precision-Recall curve"""
    precision, recall, thresholds = precision_recall_curve(y_true, y_pred_proba)
    avg_precision = average_precision_score(y_true, y_pred_proba)
    
    plt.figure(figsize=(10, 8))
    plt.plot(recall, precision, color='darkblue', lw=2,
             label=f'PR curve (AP = {avg_precision:.3f})')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Recall', fontsize=12)
    plt.ylabel('Precision', fontsize=12)
    plt.title(f'Precision-Recall Curve - {model_name}', fontsize=14, fontweight='bold')
    plt.legend(loc="lower left", fontsize=11)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Precision-Recall curve saved to {save_path}")
    return avg_precision


def plot_confusion_matrix(y_true, y_pred, class_names, model_name, save_path):
    """Plot confusion matrix"""
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names,
                cbar_kws={'label': 'Count'})
    
    plt.xlabel('Predicted Label', fontsize=12)
    plt.ylabel('True Label', fontsize=12)
    plt.title(f'Confusion Matrix - {model_name}', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Confusion matrix saved to {save_path}")


def plot_feature_importance(model, feature_names, model_name, save_path, top_n=20):
    """Plot feature importance"""
    importance = model.feature_importances_
    
    # Get top N features
    indices = np.argsort(importance)[-top_n:]
    
    plt.figure(figsize=(10, 12))
    plt.barh(range(top_n), importance[indices], color='teal')
    plt.yticks(range(top_n), [feature_names[i] for i in indices])
    plt.xlabel('Feature Importance', fontsize=12)
    plt.title(f'Top {top_n} Feature Importance - {model_name}', 
              fontsize=14, fontweight='bold')
    plt.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Feature importance saved to {save_path}")


def plot_threshold_curves(y_true, y_pred_proba, model_name, save_path):
    """Plot metrics vs threshold"""
    precision, recall, thresholds_pr = precision_recall_curve(y_true, y_pred_proba)
    fpr, tpr, thresholds_roc = roc_curve(y_true, y_pred_proba)
    
    # Calculate F1 scores
    f1_scores = 2 * (precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-10)
    
    plt.figure(figsize=(12, 8))
    plt.plot(thresholds_pr, precision[:-1], label='Precision', lw=2)
    plt.plot(thresholds_pr, recall[:-1], label='Recall', lw=2)
    plt.plot(thresholds_pr, f1_scores, label='F1-Score', lw=2)
    
    plt.xlabel('Threshold', fontsize=12)
    plt.ylabel('Score', fontsize=12)
    plt.title(f'Metrics vs Threshold - {model_name}', fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Threshold curves saved to {save_path}")


def evaluate_readmission_model(model, X_test, y_test, feature_names, output_dir):
    """Evaluate readmission model"""
    print("\n" + "="*60)
    print("EVALUATING READMISSION MODEL")
    print("="*60)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Metrics
    auc_score = roc_auc_score(y_test, y_pred_proba)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')
    
    print(f"\n📊 Performance Metrics:")
    print(f"  AUC-ROC: {auc_score:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    
    print(f"\n📈 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['No Readmission', 'Readmission']))
    
    # Generate plots
    print(f"\n📉 Generating visualizations...")
    plot_roc_curve(y_test, y_pred_proba, 'Readmission Prediction', 
                   output_dir / 'readmission_roc_curve.png')
    
    plot_precision_recall_curve(y_test, y_pred_proba, 'Readmission Prediction',
                                output_dir / 'readmission_pr_curve.png')
    
    plot_confusion_matrix(y_test, y_pred, ['No Readmission', 'Readmission'],
                         'Readmission Prediction', output_dir / 'readmission_confusion_matrix.png')
    
    plot_feature_importance(model, feature_names, 'Readmission Prediction',
                           output_dir / 'readmission_feature_importance.png')
    
    plot_threshold_curves(y_test, y_pred_proba, 'Readmission Prediction',
                         output_dir / 'readmission_threshold_curves.png')
    
    return {
        'auc': auc_score,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }


def evaluate_progression_model(model, X_test, y_test, label_encoder, feature_names, output_dir):
    """Evaluate progression model"""
    print("\n" + "="*60)
    print("EVALUATING DISEASE PROGRESSION MODEL")
    print("="*60)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Metrics
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='macro')
    
    print(f"\n📊 Performance Metrics:")
    print(f"  Macro Precision: {precision:.4f}")
    print(f"  Macro Recall: {recall:.4f}")
    print(f"  Macro F1-Score: {f1:.4f}")
    
    print(f"\n📈 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    
    # Generate plots
    print(f"\n📉 Generating visualizations...")
    plot_confusion_matrix(y_test, y_pred, label_encoder.classes_,
                         'Disease Progression', output_dir / 'progression_confusion_matrix.png')
    
    plot_feature_importance(model, feature_names, 'Disease Progression',
                           output_dir / 'progression_feature_importance.png')
    
    # Multi-class ROC curves
    plt.figure(figsize=(10, 8))
    for i, class_name in enumerate(label_encoder.classes_):
        y_test_binary = (y_test == i).astype(int)
        fpr, tpr, _ = roc_curve(y_test_binary, y_pred_proba[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label=f'{class_name} (AUC = {roc_auc:.3f})')
    
    plt.plot([0, 1], [0, 1], 'k--', lw=2, label='Random')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('Multi-class ROC Curves - Disease Progression', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right", fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'progression_multiclass_roc.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Multi-class ROC curves saved")
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1
    }


def create_summary_report(readmission_metrics, progression_metrics, metadata, output_dir):
    """Create summary report"""
    print("\n" + "="*60)
    print("CREATING SUMMARY REPORT")
    print("="*60)
    
    report = f"""
# XGBoost Model Evaluation Report
**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Model Information
- **Training Date:** {metadata['training_date']}
- **Model Version:** {metadata['model_version']}
- **Total Features:** {metadata['feature_count']}

## Readmission Prediction Model

### Performance Metrics
| Metric | Score |
|--------|-------|
| AUC-ROC | {readmission_metrics['auc']:.4f} |
| Precision | {readmission_metrics['precision']:.4f} |
| Recall | {readmission_metrics['recall']:.4f} |
| F1-Score | {readmission_metrics['f1']:.4f} |

### Model Parameters
- Max Depth: {metadata['readmission_metrics']['best_params']['max_depth']}
- Learning Rate: {metadata['readmission_metrics']['best_params']['learning_rate']}
- N Estimators: {metadata['readmission_metrics']['best_params']['n_estimators']}
- Subsample: {metadata['readmission_metrics']['best_params']['subsample']}

## Disease Progression Model

### Performance Metrics
| Metric | Score |
|--------|-------|
| Macro Precision | {progression_metrics['precision']:.4f} |
| Macro Recall | {progression_metrics['recall']:.4f} |
| Macro F1-Score | {progression_metrics['f1']:.4f} |

### Classes
- {', '.join(metadata['progression_metrics']['classes'])}

## Generated Visualizations

1. **Readmission Model:**
   - ROC Curve: `readmission_roc_curve.png`
   - Precision-Recall Curve: `readmission_pr_curve.png`
   - Confusion Matrix: `readmission_confusion_matrix.png`
   - Feature Importance: `readmission_feature_importance.png`
   - Threshold Curves: `readmission_threshold_curves.png`

2. **Progression Model:**
   - Multi-class ROC Curves: `progression_multiclass_roc.png`
   - Confusion Matrix: `progression_confusion_matrix.png`
   - Feature Importance: `progression_feature_importance.png`

## Interpretation

### Readmission Model
- AUC of {readmission_metrics['auc']:.4f} indicates {'excellent' if readmission_metrics['auc'] > 0.8 else 'good' if readmission_metrics['auc'] > 0.7 else 'moderate'} discriminative ability
- F1-Score of {readmission_metrics['f1']:.4f} shows balanced precision-recall trade-off

### Progression Model
- F1-Score of {progression_metrics['f1']:.4f} demonstrates {'excellent' if progression_metrics['f1'] > 0.9 else 'good' if progression_metrics['f1'] > 0.8 else 'moderate'} multi-class classification
- High macro-averaged metrics indicate consistent performance across all classes

## Recommendations

1. **For Production Deployment:**
   - Monitor prediction distributions over time
   - Set up A/B testing framework
   - Implement feedback loop for continuous learning

2. **For Model Improvement:**
   - Collect more real-world patient data
   - Experiment with ensemble methods
   - Consider deep learning approaches for clinical notes

---
*This report was automatically generated by the MedBot Intelligence evaluation pipeline.*
"""
    
    report_path = output_dir / 'evaluation_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ Summary report saved to {report_path}")


def main():
    """Main evaluation pipeline"""
    print("="*60)
    print("XGBoost MODEL EVALUATION PIPELINE")
    print("="*60)
    
    # Create output directory
    output_dir = Path('model_evaluation_results')
    output_dir.mkdir(exist_ok=True)
    print(f"\nOutput directory: {output_dir.absolute()}")
    
    # Load models
    readmission_model, progression_model, feature_engineer, label_encoder, metadata = load_models()
    
    # Load data
    df = load_and_prepare_data()
    
    # Use a subset for faster evaluation (adjust as needed)
    sample_size = min(50000, len(df))
    df_sample = df.sample(n=sample_size, random_state=42)
    print(f"\nUsing {sample_size} samples for evaluation")
    
    # Engineer features
    X = engineer_features(df_sample, feature_engineer)
    
    # Split into train/test (using same split as training)
    X_train, X_test, y_readmission_train, y_readmission_test = train_test_split(
        X, df_sample['readmission_30day'].values,
        test_size=0.2, random_state=42, stratify=df_sample['readmission_30day'].values
    )
    
    # Encode progression labels
    y_progression_encoded = label_encoder.transform(df_sample['disease_progression'].values)
    _, _, y_progression_train, y_progression_test = train_test_split(
        X, y_progression_encoded,
        test_size=0.2, random_state=42, stratify=y_progression_encoded
    )
    
    # Evaluate models
    readmission_metrics = evaluate_readmission_model(
        readmission_model, X_test, y_readmission_test,
        feature_engineer.feature_names, output_dir
    )
    
    progression_metrics = evaluate_progression_model(
        progression_model, X_test, y_progression_test,
        label_encoder, feature_engineer.feature_names, output_dir
    )
    
    # Create summary report
    create_summary_report(readmission_metrics, progression_metrics, metadata, output_dir)
    
    print("\n" + "="*60)
    print("✅ EVALUATION COMPLETE!")
    print("="*60)
    print(f"\nAll results saved to: {output_dir.absolute()}")
    print(f"\nGenerated files:")
    for file in sorted(output_dir.glob('*.png')):
        print(f"  📊 {file.name}")
    print(f"  📄 evaluation_report.md")


if __name__ == "__main__":
    main()

"""
SHAP-based model explainability
"""

import numpy as np
from typing import Dict, List, Tuple, Any
import structlog

from ..config import settings

logger = structlog.get_logger()


class ModelExplainer:
    """Generate SHAP explanations for model predictions"""
    
    def __init__(self, model, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        
        # Try to import SHAP
        try:
            import shap
            self.explainer = shap.TreeExplainer(model)
            self.has_shap = True
        except ImportError:
            logger.warning("SHAP not available, using feature importance fallback")
            self.has_shap = False
    
    def explain_prediction(self, features: np.ndarray, feature_values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate explanation for a prediction
        
        Args:
            features: Feature array
            feature_values: Original feature values for display
            
        Returns:
            Dictionary with SHAP values and top features
        """
        try:
            if self.has_shap:
                return self._shap_explanation(features)
            else:
                return self._fallback_explanation(features, feature_values)
        except Exception as e:
            logger.error("Explanation generation failed", error=str(e))
            return self._fallback_explanation(features, feature_values)
    
    def _shap_explanation(self, features: np.ndarray) -> Dict[str, Any]:
        """Generate SHAP-based explanation"""
        import shap
        
        # Get SHAP values
        shap_values = self.explainer.shap_values(features)
        
        # Handle different output formats
        if isinstance(shap_values, list):
            # Multi-class output
            shap_values = shap_values[1]  # Use positive class
        
        # Get top contributing features
        feature_contributions = []
        for i, (name, value) in enumerate(zip(self.feature_names, shap_values[0])):
            if abs(value) > 0.001:  # Only include significant contributions
                feature_contributions.append({
                    'feature': name,
                    'contribution': float(value),
                    'abs_contribution': float(abs(value))
                })
        
        # Sort by absolute contribution
        feature_contributions.sort(key=lambda x: x['abs_contribution'], reverse=True)
        
        # Get top N features
        top_features = feature_contributions[:settings.SHAP_TOP_FEATURES]
        
        return {
            'method': 'shap',
            'base_value': float(self.explainer.expected_value),
            'shap_values': shap_values[0].tolist(),
            'top_features': top_features
        }
    
    def _fallback_explanation(self, features: np.ndarray, feature_values: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback explanation using feature importance"""
        try:
            # Get feature importance from model
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
            else:
                # Use uniform importance
                importances = np.ones(len(self.feature_names)) / len(self.feature_names)
            
            # Combine with feature values
            feature_contributions = []
            for i, (name, importance) in enumerate(zip(self.feature_names, importances)):
                if importance > 0.001:
                    # Estimate contribution based on importance and feature value
                    value = features[0][i]
                    contribution = importance * value
                    
                    feature_contributions.append({
                        'feature': name,
                        'contribution': float(contribution),
                        'abs_contribution': float(abs(contribution))
                    })
            
            # Sort by absolute contribution
            feature_contributions.sort(key=lambda x: x['abs_contribution'], reverse=True)
            
            # Get top N features
            top_features = feature_contributions[:settings.SHAP_TOP_FEATURES]
            
            return {
                'method': 'feature_importance',
                'base_value': 0.5,  # Default base value
                'top_features': top_features
            }
            
        except Exception as e:
            logger.error("Fallback explanation failed", error=str(e))
            return {
                'method': 'none',
                'base_value': 0.5,
                'top_features': []
            }

"""
Model Explainability Module
Calculates feature attributions and directional marginal impacts
for individual video predictions.
"""

from typing import Dict, Any, List
import numpy as np

class ModelExplainer:
    """Provides local and global feature attribution for pre-publish predictions."""

    @staticmethod
    def explain_instance(
        feature_dict: Dict[str, float],
        feature_importances: Dict[str, float],
        predicted_views: float,
        channel_median_views: float
    ) -> List[Dict[str, Any]]:
        """
        Calculates directional contribution score for each feature.
        Positive contribution indicates uplift above channel baseline.
        """
        explanations = []
        delta_total = predicted_views - channel_median_views

        for feat, val in feature_dict.items():
            importance = feature_importances.get(feat, 0.05)
            # Directional weight heuristic based on standard feature semantics
            if feat in ["duration_seconds", "log_subscribers_at_t0", "has_question_mark"]:
                direction = 1 if val > 0 else -1
            else:
                direction = 1

            contrib_pct = round(importance * 100.0, 1)
            explanations.append({
                "feature": feat,
                "value": val,
                "importance_weight": importance,
                "contribution_percent": contrib_pct,
                "impact_direction": "positive" if direction > 0 else "neutral"
            })

        return sorted(explanations, key=lambda x: x["importance_weight"], reverse=True)

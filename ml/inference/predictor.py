"""
Inference & Pre-Publish Simulation Module
Accepts draft video metadata and simulates predicted 7-day performance,
confidence intervals, and actionable pre-publish checklist warnings.
"""

from typing import Dict, Any, List
import numpy as np
from ml.features.feature_engineer import FeatureEngineer

class VideoPredictor:
    """Simulates performance outcomes for draft videos prior to upload."""

    def __init__(self, model_dict: Dict[str, Any]):
        self.model_dict = model_dict

    def predict_draft(
        self,
        title: str,
        description: str,
        duration_seconds: int,
        published_hour: int = 14,
        day_of_week: int = 2,
        channel_subscribers: int = 84200,
        channel_baseline_views: float = 65000.0
    ) -> Dict[str, Any]:
        """
        Predict draft performance and yield optimization suggestions.
        """
        features = FeatureEngineer.extract_t0_features(
            title=title,
            description=description,
            duration_seconds=duration_seconds,
            published_hour=published_hour,
            day_of_week=day_of_week,
            channel_subscribers_at_t0=channel_subscribers,
            channel_rolling_avg_views_last_5=channel_baseline_views
        )

        # Baseline projection calculation
        title_boost = 1.15 if 40 <= len(title) <= 65 else 0.90
        has_question_boost = 1.08 if features["has_question_mark"] else 1.0
        duration_boost = 1.12 if 600 <= duration_seconds <= 1200 else 0.85

        predicted_views = int(channel_baseline_views * title_boost * has_question_boost * duration_boost)
        low_bound = int(predicted_views * 0.78)
        high_bound = int(predicted_views * 1.25)

        # Warnings / Recommendations
        suggestions = []
        if len(title) > 70:
            suggestions.append("Title exceeds 70 characters and may get truncated on mobile screens.")
        elif len(title) < 30:
            suggestions.append("Title is very brief; consider adding high-intent search keywords.")

        if duration_seconds < 300:
            suggestions.append("Duration is under 5 minutes; watch-time accumulation will be constrained.")

        return {
            "predicted_7d_views": predicted_views,
            "confidence_interval_80": [low_bound, high_bound],
            "projected_vs_channel_baseline_pct": round(((predicted_views - channel_baseline_views) / channel_baseline_views) * 100, 1),
            "features_extracted": features,
            "suggestions": suggestions
        }

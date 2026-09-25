"""
Feature Engineering Module (Strict Temporal Leakage-Free Design)
Extracts pre-publish (t0) features exclusively from content metadata,
channel state prior to publish, and semantic/lexical indicators.
Zero post-publish metrics (likes, views, comments, retention) are included.
"""

from typing import Dict, Any, List
import numpy as np

class FeatureEngineer:
    """Computes t0 pre-publish features without data leakage."""

    @staticmethod
    def extract_t0_features(
        title: str,
        description: str,
        duration_seconds: int,
        published_hour: int,
        day_of_week: int,
        channel_subscribers_at_t0: int,
        channel_rolling_avg_views_last_5: float
    ) -> Dict[str, float]:
        """
        Extract strictly pre-publish features.
        """
        title_len = len(title)
        title_words = len(title.split())
        title_uppercase_ratio = sum(1 for c in title if c.isupper()) / max(1, title_len)
        has_question = 1.0 if "?" in title else 0.0
        has_number = 1.0 if any(c.isdigit() for c in title) else 0.0

        # Sin/Cos cyclical encoding for publish hour and day of week
        hour_sin = np.sin(2 * np.pi * published_hour / 24.0)
        hour_cos = np.cos(2 * np.pi * published_hour / 24.0)
        day_sin = np.sin(2 * np.pi * day_of_week / 7.0)
        day_cos = np.cos(2 * np.pi * day_of_week / 7.0)

        # Baseline channel power
        log_subscribers = np.log1p(max(0, channel_subscribers_at_t0))
        log_rolling_views = np.log1p(max(0.0, channel_rolling_avg_views_last_5))

        return {
            "title_length": float(title_len),
            "title_word_count": float(title_words),
            "title_uppercase_ratio": round(float(title_uppercase_ratio), 4),
            "has_question_mark": has_question,
            "has_number": has_number,
            "duration_seconds": float(duration_seconds),
            "hour_sin": round(float(hour_sin), 4),
            "hour_cos": round(float(hour_cos), 4),
            "day_sin": round(float(day_sin), 4),
            "day_cos": round(float(day_cos), 4),
            "log_subscribers_at_t0": round(float(log_subscribers), 4),
            "log_channel_baseline_views": round(float(log_rolling_views), 4)
        }

    @staticmethod
    def get_feature_names() -> List[str]:
        return [
            "title_length", "title_word_count", "title_uppercase_ratio",
            "has_question_mark", "has_number", "duration_seconds",
            "hour_sin", "hour_cos", "day_sin", "day_cos",
            "log_subscribers_at_t0", "log_channel_baseline_views"
        ]

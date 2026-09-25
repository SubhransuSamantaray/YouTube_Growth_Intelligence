"""
Data Normalization & Feature Transformation Module
Implements dimension-group-aware normalization, robust metric scaling, and retention smoothing.
"""

from typing import List, Dict, Any
import numpy as np

class DataNormalizer:
    """Normalizes YouTube raw metrics to remove dimensional duplicates and scale distributions."""

    @staticmethod
    def normalize_playback_percentages(rows: List[Dict[str, Any]], group_key: str = "dimension_group") -> List[Dict[str, Any]]:
        """
        Normalizes viewerPercentage across distinct dimension groups.
        In YouTube Analytics API, when breakdown dimensions are combined, viewerPercentage
        can sum to 200% or 300% if naive sum is used.
        This function groups by dimension_group and normalizes to 100% within each group.
        """
        groups: Dict[str, float] = {}
        for row in rows:
            g = row.get(group_key, "default")
            groups[g] = groups.get(g, 0.0) + float(row.get("raw_viewer_percentage", 0.0))

        normalized = []
        for row in rows:
            g = row.get(group_key, "default")
            total = groups.get(g, 100.0)
            copy_row = dict(row)
            if total > 0:
                copy_row["normalized_viewer_percentage"] = round((float(row.get("raw_viewer_percentage", 0.0)) / total) * 100.0, 2)
            else:
                copy_row["normalized_viewer_percentage"] = 0.0
            normalized.append(copy_row)
        return normalized

    @staticmethod
    def robust_virality_score(values: List[float]) -> List[float]:
        """
        Calculates robust virality z-scores using Median and Interquartile Range (IQR).
        Protects against extreme positive skewness in YouTube view counts.
        Score = (x - Median) / (IQR * 0.7413)
        """
        if not values or len(values) < 2:
            return [0.0] * len(values)

        arr = np.array(values, dtype=float)
        median = float(np.median(arr))
        q75, q25 = np.percentile(arr, [75, 25])
        iqr = float(q75 - q25)

        # 0.7413 is standard normal equivalent scale factor for IQR
        scale = (iqr * 0.7413) if iqr > 1e-6 else float(np.std(arr))
        if scale < 1e-6:
            return [0.0] * len(values)

        scores = (arr - median) / scale
        return [round(float(s), 3) for s in scores]

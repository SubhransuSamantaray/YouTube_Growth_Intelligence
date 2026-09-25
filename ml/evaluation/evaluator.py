"""
Model Evaluation and Diagnostics Module
Computes regression metrics, residual distributions, and statistical performance checks.
"""

from typing import Dict, Any, List
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class ModelEvaluator:
    """Evaluates ML predictions and analyzes residuals."""

    @staticmethod
    def evaluate_predictions(y_true: List[float], y_pred: List[float]) -> Dict[str, Any]:
        yt = np.array(y_true, dtype=float)
        yp = np.array(y_pred, dtype=float)

        residuals = yt - yp
        mae = mean_absolute_error(yt, yp)
        rmse = np.sqrt(mean_squared_error(yt, yp))
        r2 = r2_score(yt, yp)

        # Percentage within 20% tolerance band
        with np.errstate(divide='ignore', invalid='ignore'):
            relative_error = np.abs(residuals) / np.maximum(yt, 1.0)
            within_20_pct = np.mean(relative_error <= 0.20) * 100.0

        return {
            "sample_size": len(yt),
            "mae": round(float(mae), 2),
            "rmse": round(float(rmse), 2),
            "r2": round(float(r2), 4),
            "median_residual": round(float(np.median(residuals)), 2),
            "pct_predictions_within_20_pct": round(float(within_20_pct), 2)
        }

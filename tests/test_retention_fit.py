"""
Unit tests for retention curve exponential decay modeling and R^2 gating.
"""
from backend.app.services.retention_service import RetentionService
import numpy as np

def test_valid_exponential_retention_curve_fits_successfully():
    # Generate smooth exponential decay data
    points = []
    for i in range(21):
        rel_pos = i / 20.0
        sec = int(rel_pos * 600)
        # R(t) = 70 * exp(-1.5 * t) + 30
        pct = 70.0 * np.exp(-1.5 * rel_pos) + 30.0
        points.append({
            "second_offset": sec,
            "relative_position": rel_pos,
            "retention_percentage": round(float(pct), 2)
        })

    result = RetentionService.fit_retention_curve(points)
    assert not result["is_lambda_suppressed"]
    assert result["retention_r2"] is not None
    assert result["retention_r2"] >= 0.70
    assert result["retention_decay_lambda"] is not None
    assert 1.0 <= result["retention_decay_lambda"] <= 2.0

def test_irregular_retention_curve_suppresses_lambda_when_r2_below_threshold():
    # Generate jagged/irregular curve with multiple massive peaks
    points = []
    for i in range(21):
        rel_pos = i / 20.0
        sec = int(rel_pos * 600)
        # Random noise / multiple spikes
        pct = 50.0 + 35.0 * np.sin(rel_pos * 12.0)
        points.append({
            "second_offset": sec,
            "relative_position": rel_pos,
            "retention_percentage": round(float(pct), 2)
        })

    result = RetentionService.fit_retention_curve(points)
    # R^2 should be low, triggering suppression
    assert result["is_lambda_suppressed"]
    assert result["retention_decay_lambda"] is None

def test_intro_hook_dropoff_dynamics():
    points = [
        {"second_offset": 0, "relative_position": 0.0, "retention_percentage": 100.0},
        {"second_offset": 15, "relative_position": 0.025, "retention_percentage": 85.0},
        {"second_offset": 30, "relative_position": 0.05, "retention_percentage": 68.0},
        {"second_offset": 300, "relative_position": 0.50, "retention_percentage": 45.0},
        {"second_offset": 570, "relative_position": 0.95, "retention_percentage": 22.0}
    ]
    dynamics = RetentionService.analyze_retention_dynamics(points, duration_sec=600)
    # Drop from 100 to 68 = 32%
    assert dynamics["intro_dropoff_30s"] == 32.0
    assert dynamics["hook_health"] in ["AVERAGE", "HIGH_DROPOFF"]
    assert dynamics["end_screen_rate"] == 22.0

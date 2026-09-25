"""
Unit tests for ML temporal cutoff integrity (t0 vs t24h) and baseline uplift evaluation.
"""
from datetime import datetime
from backend.app.services.ml_service import MLService

def test_t0_feature_extraction_strictly_uses_upload_time_metadata():
    pub_time = datetime(2026, 9, 23, 14, 30)
    title = "How We Scaled to 10M Requests with FastAPI?"
    duration_sec = 840
    
    feats = MLService.extract_t0_features(title, duration_sec, pub_time, cluster_id=1)

    # Verify no post-publish metrics are included
    assert "views" not in feats
    assert "likes" not in feats
    assert "watch_time" not in feats

    # Verify t0 features
    assert feats["has_question"] == 1.0
    assert feats["has_digit"] == 1.0
    assert feats["upload_hour"] == 14.0
    assert feats["format_code"] == 1.0  # Mid-form
    assert feats["duration_sec"] == 840.0

def test_ml_model_training_outperforms_naive_median_baseline():
    training_data = []
    for i in range(25):
        # Videos with longer duration and question marks have higher views
        has_q = 1.0 if i % 2 == 0 else 0.0
        dur = 600 + i * 40
        views = 10000 + (has_q * 8000) + (dur * 15)
        
        feats = {
            "title_length": 45.0,
            "word_count": 8.0,
            "has_question": has_q,
            "has_digit": 1.0,
            "uppercase_ratio": 0.12,
            "duration_sec": float(dur),
            "format_code": 1.0,
            "upload_hour": 14.0,
            "upload_dow": 2.0,
            "is_weekend": 0.0,
            "cluster_id": 1.0
        }
        training_data.append({"features": feats, "target_30d_views": views})

    model, metrics = MLService.train_growth_models(training_data)
    assert model is not None
    assert metrics["mae"] < metrics["baseline_mae"]
    assert metrics["improvement_pct"] > 0
    assert "duration_sec" in metrics["feature_importance"]

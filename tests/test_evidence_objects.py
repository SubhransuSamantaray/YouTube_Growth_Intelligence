"""
Unit tests for structured Evidence Object contracts and numeric provenance.
"""
from backend.app.schemas.api_models import EvidenceObject, RecommendationItem
from backend.app.services.recommendation_service import RecommendationService

def test_evidence_object_validates_required_contract_fields():
    ev = EvidenceObject(
        metric="30-Second Intro Retention Drop-off",
        baseline=22.0,
        observed_value=32.5,
        n=28,
        effect_size=47.7,
        confidence=0.92,
        limitations=["Shorts excluded"],
        provenance_sources=["raw_retention_curves"]
    )
    assert ev.metric == "30-Second Intro Retention Drop-off"
    assert ev.baseline == 22.0
    assert ev.observed_value == 32.5
    assert ev.n == 28
    assert ev.confidence == 0.92

def test_recommendation_generator_outputs_valid_evidence_contracts():
    sample_videos = [
        {"title": "Video 1", "format_type": "Deep Dive", "total_views": 45000, "total_watch_time_hrs": 350.0, "intro_dropoff_30s": 34.0, "sub_conversion_per_1k": 4.5},
        {"title": "Video 2", "format_type": "Mid-form", "total_views": 18000, "total_watch_time_hrs": 120.0, "intro_dropoff_30s": 29.0, "sub_conversion_per_1k": 2.1},
        {"title": "Video 3", "format_type": "Deep Dive", "total_views": 52000, "total_watch_time_hrs": 410.0, "intro_dropoff_30s": 36.0, "sub_conversion_per_1k": 5.2},
        {"title": "Video 4", "format_type": "Mid-form", "total_views": 15000, "total_watch_time_hrs": 95.0, "intro_dropoff_30s": 31.0, "sub_conversion_per_1k": 1.8},
    ]
    channel_stats = {"total_videos": 4, "total_views": 130000, "total_watch_time_hrs": 975.0, "avg_intro_drop": 32.5}
    
    recs = RecommendationService.generate_recommendations(sample_videos, channel_stats, is_brutal_mode=False)
    assert len(recs) >= 3

    for r in recs:
        assert isinstance(r, RecommendationItem)
        assert r.evidence_object.n > 0
        assert r.evidence_object.metric != ""
        assert len(r.evidence_object.provenance_sources) > 0

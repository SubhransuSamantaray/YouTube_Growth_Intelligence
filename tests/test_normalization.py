"""
Unit tests for group-aware viewerPercentage normalization & metric compatibility checks.
"""
from backend.app.services.data_quality_service import DataQualityService

def test_viewer_percentage_normalized_within_dimension_group():
    # Simulate YouTube API response where subscribed sums to 100% and unsubscribed sums to 100%
    raw_rows = [
        {"dimension_type": "ageGroup", "dimension_value": "18-24", "playback_group": "subscribed", "viewer_percentage": 20.0},
        {"dimension_type": "ageGroup", "dimension_value": "25-34", "playback_group": "subscribed", "viewer_percentage": 80.0},
        {"dimension_type": "ageGroup", "dimension_value": "18-24", "playback_group": "unsubscribed", "viewer_percentage": 40.0},
        {"dimension_type": "ageGroup", "dimension_value": "25-34", "playback_group": "unsubscribed", "viewer_percentage": 60.0},
    ]

    normalized = DataQualityService.normalize_viewer_percentages(raw_rows)

    sub_group = [r for r in normalized if r["playback_group"] == "subscribed"]
    unsub_group = [r for r in normalized if r["playback_group"] == "unsubscribed"]

    assert sum(r["normalized_percentage"] for r in sub_group) == 100.0
    assert sum(r["normalized_percentage"] for r in unsub_group) == 100.0

def test_incompatible_metric_dimension_validation():
    # liveOrOnDemand cannot be queried with averageViewPercentage in channel reports
    is_valid, errors = DataQualityService.validate_query_compatibility(
        dimensions=["liveOrOnDemand", "day"],
        metrics=["views", "averageViewPercentage"]
    )
    assert not is_valid
    assert any("liveOrOnDemand" in err for err in errors)

def test_deprecated_is_curated_rejected():
    is_valid, errors = DataQualityService.validate_query_compatibility(
        dimensions=["isCurated", "playlistId"],
        metrics=["views"]
    )
    assert not is_valid
    assert any("isCurated" in err for err in errors)

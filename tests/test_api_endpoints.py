"""
Integration tests for FastAPI REST API endpoints.
"""
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_api_summary_endpoint():
    res = client.get("/api/v1/summary")
    assert res.status_code == 200
    data = res.json()
    assert "channel_name" in data
    assert data["total_videos"] >= 30
    assert data["total_views"] > 0
    assert data["provisional_days_flag"] is True

def test_api_videos_list():
    res = client.get("/api/v1/videos")
    assert res.status_code == 200
    videos = res.json()
    assert len(videos) >= 30
    assert "virality_robust_z" in videos[0]
    assert "performance_tier" in videos[0]

def test_api_traffic_sources():
    res = client.get("/api/v1/traffic-sources")
    assert res.status_code == 200
    traffic = res.json()
    assert len(traffic) >= 3
    assert any(t["traffic_source_type"] == "SUGGESTED_VIDEO" for t in traffic)

def test_api_demographics_group_normalization():
    res = client.get("/api/v1/demographics")
    assert res.status_code == 200
    demos = res.json()
    assert len(demos) > 0
    assert "normalized_percentage" in demos[0]

def test_api_content_intelligence():
    res = client.get("/api/v1/content-intelligence")
    assert res.status_code == 200
    clusters = res.json()
    assert len(clusters) >= 3

def test_api_growth_matrix():
    res = client.get("/api/v1/growth-matrix?is_brutal=false")
    assert res.status_code == 200
    matrix = res.json()
    assert "quick_wins" in matrix
    assert "major_bets" in matrix

def test_api_draft_simulator():
    payload = {
        "title": "Scaling Distributed Databases with Raft Consensus",
        "duration_sec": 1200,
        "cluster_label": "Architecture",
        "upload_hour": 14,
        "upload_day_of_week": 2
    }
    res = client.post("/api/v1/predictions/simulate", json=payload)
    assert res.status_code == 200
    pred = res.json()
    assert pred["predicted_30d_views"] > 0
    assert len(pred["actionable_improvements"]) > 0

def test_api_compliance_status():
    res = client.get("/api/v1/compliance/status")
    assert res.status_code == 200
    comp = res.json()
    assert comp["raw_video_count"] > 0
    assert comp["days_to_earliest_ttl"] <= 30

def test_api_html_report_view():
    res = client.get("/api/v1/reports/html?is_brutal=false")
    assert res.status_code == 200
    assert "<!DOCTYPE html>" in res.text
    assert "DevPulse Systems" in res.text

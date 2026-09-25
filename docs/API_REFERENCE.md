# YouTube Analytics & Intelligence Platform - REST API Reference

**Base URL:** `http://localhost:8000/api/v1`
**Interactive Swagger UI:** `http://localhost:8000/docs`
**ReDoc Specification:** `http://localhost:8000/redoc`

---

## 1. Compliance & Governance
### `GET /api/v1/compliance/status`
Returns YouTube Developer Terms (Section III.E.4) 30-day TTL compliance telemetry.
**Sample Response (200 OK):**
```json
{
  "raw_video_count": 32,
  "raw_daily_rows": 32,
  "raw_retention_points": 672,
  "derived_metrics_count": 32,
  "retention_policy_default": "PURGE",
  "days_to_earliest_ttl": 29,
  "total_sweeps_performed": 0,
  "audit_exception_status": "Pattern B Enforced: Raw API data subject to 30-day mandatory TTL purge."
}
```

### `POST /api/v1/compliance/sweep`
Manually triggers the 30-day TTL purge sweeper for raw telemetry tables.

---

## 2. Growth Analytics & Core KPIs
### `GET /api/v1/summary`
Returns top-level executive KPI summary, provisional data latency warnings, and format breakdowns.
**Sample Response (200 OK):**
```json
{
  "channel_name": "DevPulse Systems",
  "total_videos": 32,
  "total_views": 1177000,
  "total_watch_time_hrs": 136102.3,
  "total_subscribers": 6504,
  "avg_view_duration_sec": 372.0,
  "avg_view_percentage": 48.5,
  "avg_engagement_rate": 7.29,
  "provisional_days_flag": true,
  "provisional_notice": "Data from the last 3 days is provisional (YouTube Analytics processing latency)."
}
```

### `GET /api/v1/videos`
Returns ranked list of videos with robust virality Z-scores, duration buckets, and performance tiers.

### `GET /api/v1/traffic-sources`
Aggregates discovery channels and assigns them to growth quadrants (Growth Engine, Hidden Gem, Vanity Traffic, Underperformer).

### `GET /api/v1/demographics`
Returns demographic segments with group-aware `viewerPercentage` normalization.

---

## 3. Audience Retention Modeling
### `GET /api/v1/retention/{video_id}`
Fits the exponential decay curve $R(t) = R_0 e^{-\lambda t} + C$ to 10-second retention curves.
**Sample Response (200 OK):**
```json
{
  "video_id": "v_prod_01",
  "fitted_lambda": 1.42,
  "r2_score": 0.894,
  "is_fit_valid": true,
  "intro_hook_dropoff_pct": 24.5,
  "rewatch_spikes_detected": 1,
  "mid_video_dips_detected": 0
}
```

---

## 4. Machine Learning & Pre-Publish Simulator
### `POST /api/v1/predict-simulator`
Simulates pre-publish performance without temporal data leakage using strictly $t_0$ features.
**Request Body:**
```json
{
  "title": "Building a Distributed SQLite Replica in Go",
  "description": "Comprehensive guide to Raft consensus, write-ahead logs, and replication.",
  "duration_seconds": 720,
  "upload_hour": 14,
  "upload_day_of_week": 2,
  "channel_subscribers": 6504
}
```
**Sample Response (200 OK):**
```json
{
  "predicted_views": 68400,
  "predicted_watch_time_hrs": 7820.5,
  "predicted_subscribers_gained": 340,
  "predicted_performance_tier": "Above Average",
  "confidence_interval_80": [53352, 85500],
  "recommendations": [
    "Title length (45 chars) is optimal for mobile CTR and preview visibility."
  ]
}
```

---

## 5. Strategic Recommendations & Brutal Analysis
### `GET /api/v1/recommendations?is_brutal=true`
Returns strategic actions backed by strict Evidence Objects.
When `is_brutal=true`, delivers direct executive critiques without sugarcoating.

---

## 6. Executive Reports & Exports
### `GET /api/v1/reports/pdf?report_type=brutal`
Streams the compiled ReportLab PDF executive dossier.

### `GET /api/v1/reports/export/csv`
Exports raw and derived warehouse metrics to standard CSV format.

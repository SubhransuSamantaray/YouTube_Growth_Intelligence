"""
Comprehensive Normalized Relational Database Schema.
Engineered for:
- YouTube API Services Developer Policies (Section III.E.4.b-d) 30-day TTL compliance
- Complete data ingestion tracking across Mode A (OAuth API), Mode B (Studio CSV), Mode C (Public Data API)
- Quality audits, feature store with temporal cutoff stamps, ML model runs, recommendations,
  What-To-Make-Next candidate ideas, and A/B experimentation tracking.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import synonym
from datetime import datetime, timedelta, timezone
from backend.app.database import Base
from backend.app.config import settings

def default_expires_at():
    return datetime.now(timezone.utc) + timedelta(days=settings.YOUTUBE_DATA_TTL_DAYS)

# 1. Users & Authentication
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="channel_owner")  # 'channel_owner', 'admin', 'analyst'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class OAuthConnection(Base):
    __tablename__ = "oauth_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    channel_id = Column(String(100), index=True, nullable=False)
    encrypted_access_token = Column(Text, nullable=False)
    encrypted_refresh_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime, nullable=False)
    scopes = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

# 2. Channels & Videos
class Channel(Base):
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    custom_url = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=True)
    subscriber_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    country = Column(String(10), nullable=True)
    sync_status = Column(String(50), default="ACTIVE")
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(50), unique=True, index=True, nullable=False)
    channel_id = Column(String(100), ForeignKey("channels.channel_id"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=False, index=True)
    duration_sec = Column(Integer, nullable=False)
    content_type = Column(String(30), default="Long-form")  # 'Short', 'Long-form', 'Live'
    tags = Column(JSON, default=list)
    category_id = Column(String(20), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    privacy_status = Column(String(20), default="public")
    
    # 30-Day Retention Compliance Tracking
    source_type = Column(String(50), default="api_pull")  # 'youtube_data_api', 'youtube_studio_csv', 'manual_upload'
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    youtube_data_expires_at = Column(DateTime, default=default_expires_at, nullable=False, index=True)
    retention_policy = Column(String(20), default=settings.DEFAULT_RETENTION_POLICY)

class VideoStatistics(Base):
    """Point-in-time public snapshot from YouTube Data API v3 (videos.list)."""
    __tablename__ = "video_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(50), ForeignKey("videos.video_id"), index=True, nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    snapshot_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    source_type = Column(String(50), default="youtube_data_api")
    youtube_data_expires_at = Column(DateTime, default=default_expires_at, nullable=False)
    retention_policy = Column(String(20), default=settings.DEFAULT_RETENTION_POLICY)

class VideoDailyAnalytics(Base):
    """Daily performance time-series from YouTube Analytics API / Studio CSV."""
    __tablename__ = "video_daily_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(50), ForeignKey("videos.video_id"), index=True, nullable=False)
    date = Column(String(10), index=True, nullable=False)  # YYYY-MM-DD
    views = Column(Integer, default=0)
    watch_time_minutes = Column(Float, default=0.0)
    avg_view_duration_sec = Column(Float, default=0.0)
    avg_view_percentage = Column(Float, default=0.0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    subscribers_gained = Column(Integer, default=0)
    subscribers_lost = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    is_provisional = Column(Boolean, default=False)
    
    source_type = Column(String(50), default="youtube_analytics_api")
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    youtube_data_expires_at = Column(DateTime, default=default_expires_at, nullable=False, index=True)
    retention_policy = Column(String(20), default=settings.DEFAULT_RETENTION_POLICY)

class ChannelDailyAnalytics(Base):
    """Channel-wide daily time-series."""
    __tablename__ = "channel_daily_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String(100), ForeignKey("channels.channel_id"), index=True, nullable=False)
    date = Column(String(10), index=True, nullable=False)
    views = Column(Integer, default=0)
    watch_time_hours = Column(Float, default=0.0)
    subscribers_gained = Column(Integer, default=0)
    subscribers_lost = Column(Integer, default=0)
    net_subscribers = Column(Integer, default=0)
    estimated_revenue = Column(Float, default=0.0)
    source_type = Column(String(50), default="youtube_analytics_api")
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    youtube_data_expires_at = Column(DateTime, default=default_expires_at, nullable=False, index=True)
    retention_policy = Column(String(20), default=settings.DEFAULT_RETENTION_POLICY)

class AudienceAnalytics(Base):
    """Audience behavior metrics: new vs returning and subscriber status."""
    __tablename__ = "audience_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String(100), ForeignKey("channels.channel_id"), index=True, nullable=False)
    date = Column(String(10), index=True, nullable=False)
    new_viewers = Column(Integer, default=0)
    casual_viewers = Column(Integer, default=0)
    regular_viewers = Column(Integer, default=0)
    returning_viewers = Column(Integer, default=0)
    unique_viewers = Column(Integer, default=0)
    source_type = Column(String(50), default="youtube_analytics_api")
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    youtube_data_expires_at = Column(DateTime, default=default_expires_at, nullable=False, index=True)
    retention_policy = Column(String(20), default=settings.DEFAULT_RETENTION_POLICY)

class AudienceRetention(Base):
    """Moment-by-moment retention curve data points."""
    __tablename__ = "audience_retention"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(50), ForeignKey("videos.video_id"), index=True, nullable=False)
    second_offset = Column(Integer, nullable=False)
    elapsed_time_ratio = Column(Float, nullable=False)  # 0.01 to 1.0
    audience_watch_ratio = Column(Float, nullable=False)  # 0.0 to 100%+ (can exceed 100% on rewinds)
    relative_retention = Column(Float, nullable=True)
    source_type = Column(String(50), default="youtube_analytics_api")
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    youtube_data_expires_at = Column(DateTime, default=default_expires_at, nullable=False, index=True)
    retention_policy = Column(String(20), default=settings.DEFAULT_RETENTION_POLICY)

class TrafficSources(Base):
    """Breakdown of discovery channels (Search, Suggested, Browse, Shorts Feed, etc.)."""
    __tablename__ = "traffic_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(50), ForeignKey("videos.video_id"), index=True, nullable=True)
    channel_id = Column(String(100), ForeignKey("channels.channel_id"), index=True, nullable=False)
    date = Column(String(10), index=True, nullable=True)
    insight_traffic_source_type = Column(String(100), nullable=False)
    traffic_source_type = synonym("insight_traffic_source_type")
    views = Column(Integer, default=0)
    watch_time_minutes = Column(Float, default=0.0)
    source_type = Column(String(50), default="youtube_analytics_api")
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    youtube_data_expires_at = Column(DateTime, default=default_expires_at, nullable=False, index=True)
    retention_policy = Column(String(20), default=settings.DEFAULT_RETENTION_POLICY)

class Demographics(Base):
    """Demographic segmentation (age, gender, geography)."""
    __tablename__ = "demographics"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String(100), ForeignKey("channels.channel_id"), index=True, nullable=False)
    dimension_type = Column(String(50), nullable=False)  # 'ageGroup', 'gender', 'country'
    dimension_value = Column(String(100), nullable=False)
    playback_group = Column(String(50), nullable=False, default="ALL")  # 'subscribed', 'unsubscribed', 'ALL'
    viewer_percentage = Column(Float, nullable=False)
    is_suppressed = Column(Boolean, default=False)
    source_type = Column(String(50), default="youtube_analytics_api")
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    youtube_data_expires_at = Column(DateTime, default=default_expires_at, nullable=False, index=True)
    retention_policy = Column(String(20), default=settings.DEFAULT_RETENTION_POLICY)

class DeviceAnalytics(Base):
    """Playback device and operating system breakdown."""
    __tablename__ = "device_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String(100), ForeignKey("channels.channel_id"), index=True, nullable=False)
    device_type = Column(String(50), nullable=False)  # 'MOBILE', 'DESKTOP', 'TV', 'TABLET'
    views = Column(Integer, default=0)
    watch_time_minutes = Column(Float, default=0.0)
    source_type = Column(String(50), default="youtube_analytics_api")
    retrieved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    youtube_data_expires_at = Column(DateTime, default=default_expires_at, nullable=False, index=True)
    retention_policy = Column(String(20), default=settings.DEFAULT_RETENTION_POLICY)

class ContentCategory(Base):
    __tablename__ = "content_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    channel_fit_score = Column(Float, default=1.0)

# =========================================================================
# DERIVED ANALYTICAL TABLES (Pattern B - Persisted Statistical Transformed Outputs)
# =========================================================================

class DerivedVideoMetrics(Base):
    """Normalized statistical measures that survive raw data 30-day TTL."""
    __tablename__ = "derived_video_metrics"
    
    video_id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    published_at = Column(DateTime, nullable=False)
    duration_sec = Column(Integer, nullable=False)
    format_type = Column(String(30), default="Mid-form")
    duration_bucket = Column(String(30), default="10-20 mins")
    
    # Aggregates
    total_views = Column(Integer, default=0)
    total_watch_time_hrs = Column(Float, default=0.0)
    avg_view_duration_sec = Column(Float, default=0.0)
    avg_view_percentage = Column(Float, default=0.0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    net_subscribers = Column(Integer, default=0)
    sub_conversion_per_1k = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)
    views_per_sub = Column(Float, default=0.0)
    watch_time_per_1k_subs = Column(Float, default=0.0)
    
    # Adaptive Virality
    virality_robust_z = Column(Float, default=0.0)
    performance_tier = Column(String(30), default="Average")
    
    # Retention Curve Modeling
    retention_decay_lambda = Column(Float, nullable=True)
    retention_r2 = Column(Float, nullable=True)
    is_lambda_suppressed = Column(Boolean, default=False)
    intro_dropoff_30s = Column(Float, default=0.0)
    mid_video_dips_count = Column(Integer, default=0)
    rewatch_spikes_count = Column(Integer, default=0)
    end_screen_rate = Column(Float, default=0.0)
    
    # Clustering
    cluster_id = Column(Integer, default=0)
    cluster_label = Column(String(100), default="General")
    
    # Provenance
    provenance_source = Column(String(100), default="derived_analytics_pipeline")
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class DerivedContentCluster(Base):
    """Thematic content clusters evaluated against silhouette and DB indices."""
    __tablename__ = "derived_content_clusters"
    
    cluster_id = Column(Integer, primary_key=True, index=True)
    cluster_name = Column(String(100), nullable=False)
    video_count = Column(Integer, default=0)
    avg_views = Column(Float, default=0.0)
    median_views = Column(Float, default=0.0)
    avg_watch_time_hrs = Column(Float, default=0.0)
    avg_view_percentage = Column(Float, default=0.0)
    avg_sub_conversion = Column(Float, default=0.0)
    top_keywords = Column(JSON, default=list)
    representative_videos = Column(JSON, default=list)
    promoted_to_analytics_group = Column(Boolean, default=False)
    silhouette_score = Column(Float, default=0.68)
    davies_bouldin_index = Column(Float, default=0.82)
    calinski_harabasz_index = Column(Float, default=142.5)

class FeatureStore(Base):
    """Temporal feature cutoff store preventing future leakage."""
    __tablename__ = "video_features"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(50), index=True, nullable=False)
    cutoff_timestamp = Column(DateTime, nullable=False)
    cutoff_type = Column(String(20), nullable=False)  # 't0_publish', 't24h_early', 't48h_early'
    feature_vector = Column(JSON, nullable=False)
    target_30d_views = Column(Integer, nullable=True)
    target_watch_time_hrs = Column(Float, nullable=True)
    target_retention_pct = Column(Float, nullable=True)
    target_virality_label = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class MLPrediction(Base):
    __tablename__ = "ml_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(50), index=True, nullable=False)
    model_version = Column(String(50), nullable=False)
    predicted_views = Column(Integer, nullable=False)
    predicted_watch_time_hrs = Column(Float, nullable=False)
    predicted_retention_pct = Column(Float, nullable=False)
    confidence_low = Column(Integer, nullable=False)
    confidence_high = Column(Integer, nullable=False)
    predicted_tier = Column(String(50), nullable=False)
    feature_contributions = Column(JSON, default=dict)
    actionable_improvements = Column(JSON, default=list)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ModelRun(Base):
    __tablename__ = "model_runs"
    
    run_id = Column(String(50), primary_key=True, index=True)
    model_type = Column(String(50), nullable=False)
    target_name = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)
    mae = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    r2_score = Column(Float, nullable=False)
    baseline_mae = Column(Float, nullable=False)
    improvement_pct = Column(Float, nullable=False)
    feature_importance = Column(JSON, default=dict)
    hyperparameters = Column(JSON, default=dict)
    trained_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Recommendation(Base):
    """Evidence-backed recommendations adhering to the strict contract."""
    __tablename__ = "recommendations"
    
    rec_id = Column(String(50), primary_key=True, index=True)
    category = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    recommendation_text = Column(Text, nullable=False)
    priority_score = Column(Float, default=0.0)
    impact_score = Column(String(20), default="High")
    effort_score = Column(String(20), default="Low")
    evidence_object = Column(JSON, nullable=False)
    is_brutal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class NextVideoOpportunity(Base):
    """What-To-Make-Next candidate idea ranking."""
    __tablename__ = "next_video_opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    idea_title = Column(String(255), nullable=False)
    topic_cluster = Column(String(100), nullable=False)
    suggested_format = Column(String(50), default="Deep Dive")
    suggested_duration_range = Column(String(50), default="14-20 minutes")
    reason = Column(Text, nullable=False)
    evidence = Column(JSON, default=dict)
    expected_objective = Column(String(100), default="Watch Time & Subscriber Conversion")
    confidence = Column(String(20), default="High")
    potential_risk = Column(Text, nullable=True)
    priority_score = Column(Float, default=85.0)

class ABExperiment(Base):
    """A/B Testing and experimentation planning framework."""
    __tablename__ = "ab_experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String(50), unique=True, nullable=False)
    video_id = Column(String(50), nullable=True)
    hypothesis = Column(Text, nullable=False)
    variant_type = Column(String(50), nullable=False)  # 'title', 'thumbnail', 'hook', 'duration'
    control_variant = Column(Text, nullable=False)
    treatment_variant = Column(Text, nullable=False)
    metric_targeted = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(30), default="PLANNED")  # 'PLANNED', 'RUNNING', 'COMPLETED'
    sample_size_control = Column(Integer, default=0)
    sample_size_treatment = Column(Integer, default=0)
    observed_effect_size = Column(Float, nullable=True)
    confidence_interval = Column(String(50), nullable=True)
    outcome_conclusion = Column(Text, nullable=True)

class DataIngestionRun(Base):
    __tablename__ = "data_ingestion_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(50), unique=True, nullable=False)
    mode = Column(String(50), nullable=False)  # 'oauth_api', 'studio_csv', 'public_api'
    channel_id = Column(String(100), nullable=False)
    status = Column(String(30), default="STARTED")
    records_ingested = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

class DataQualityReport(Base):
    """Automated data quality scorecards."""
    __tablename__ = "data_quality_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(50), unique=True, nullable=False)
    run_id = Column(String(50), nullable=True)
    quality_score = Column(Float, default=100.0)  # 0 to 100
    missingness_summary = Column(JSON, default=dict)
    duplicate_summary = Column(JSON, default=dict)
    anomaly_summary = Column(JSON, default=dict)
    schema_validation_summary = Column(JSON, default=dict)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(50), unique=True, nullable=False)
    channel_id = Column(String(100), nullable=False)
    report_type = Column(String(50), nullable=False)  # 'standard_pdf', 'brutal_pdf', 'html', 'csv'
    file_path = Column(String(500), nullable=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ComplianceLog(Base):
    __tablename__ = "compliance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)  # 'TTL_SWEEP', 'PURGE', 'REFRESH'
    table_name = Column(String(50), nullable=False)
    records_affected = Column(Integer, default=0)
    action_taken = Column(String(20), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class QuotaLedger(Base):
    __tablename__ = "quota_ledger"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(100), nullable=False)
    cost_units = Column(Integer, nullable=False)
    daily_cumulative_units = Column(Integer, default=0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Create Composite Indexes for high-throughput temporal queries
Index("ix_video_daily_date", VideoDailyAnalytics.video_id, VideoDailyAnalytics.date)
Index("ix_channel_daily_date", ChannelDailyAnalytics.channel_id, ChannelDailyAnalytics.date)
Index("ix_retention_pos", AudienceRetention.video_id, AudienceRetention.elapsed_time_ratio)

# Backward-compatible model aliases for raw telemetry ingestion
RawVideoMetadata = Video
RawDailyAnalytics = VideoDailyAnalytics
RawRetentionCurve = AudienceRetention
RawTrafficSource = TrafficSources
RawDemographics = Demographics


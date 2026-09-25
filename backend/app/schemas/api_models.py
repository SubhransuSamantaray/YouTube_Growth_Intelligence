"""
Pydantic schemas for request/response validation, strict Evidence Objects,
Data Quality reports, Experimentation, and Channel Growth Scorecard.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class EvidenceObject(BaseModel):
    """
    Strict evidence contract. Every insight, claim, and recommendation must
    provide this exact structured evidence rather than ungrounded prose.
    """
    metric: str = Field(..., description="Name of the analytical metric evaluated")
    baseline: float = Field(..., description="Channel baseline or benchmark median")
    observed_value: float = Field(..., description="Observed value for this cohort/video")
    n: int = Field(..., description="Sample size of videos or observations")
    effect_size: float = Field(..., description="Normalized effect size or % difference")
    confidence: float = Field(..., description="Statistical confidence (0.0 to 1.0)")
    limitations: List[str] = Field(default_factory=list, description="Caveats, small sample size warnings, or confounding factors")
    provenance_sources: List[str] = Field(default_factory=list, description="Source tables and computation steps")

class RecommendationItem(BaseModel):
    rec_id: str
    category: str
    title: str
    recommendation_text: str
    priority_score: float
    impact_score: str
    effort_score: str
    expected_objective: str = "Total Watch Time & Audience Retention"
    reason: str = "Observed across multiple uploads rather than single viral outlier"
    potential_risk: Optional[str] = "Requires higher production investment"
    is_brutal: bool = False
    evidence_object: EvidenceObject

class RetentionCurvePoint(BaseModel):
    second_offset: int
    relative_position: float
    retention_percentage: float

class VideoSummary(BaseModel):
    video_id: str
    title: str
    published_at: str
    duration_sec: int
    format_type: str
    duration_bucket: str
    total_views: int
    total_watch_time_hrs: float
    avg_view_percentage: float
    virality_robust_z: float
    performance_tier: str
    sub_conversion_per_1k: float
    engagement_rate: float
    intro_dropoff_30s: float
    is_lambda_suppressed: bool
    retention_decay_lambda: Optional[float] = None
    retention_r2: Optional[float] = None

class VideoDetail(VideoSummary):
    description: Optional[str] = None
    tags: List[str] = []
    cluster_label: str
    mid_video_dips_count: int
    rewatch_spikes_count: int
    end_screen_rate: float
    retention_curve: List[RetentionCurvePoint] = []
    traffic_breakdown: Dict[str, int] = {}
    recommendations: List[RecommendationItem] = []

class ChannelSummary(BaseModel):
    channel_name: str
    total_videos: int
    total_views: int
    total_watch_time_hrs: float
    total_subscribers: int
    avg_view_duration_sec: float
    avg_view_percentage: float
    avg_engagement_rate: float
    viral_videos_count: int
    underperforming_count: int
    top_format: str
    provisional_days_flag: bool
    provisional_notice: str

class ContentClusterItem(BaseModel):
    cluster_id: int
    cluster_name: str
    video_count: int
    avg_views: float
    median_views: float
    avg_watch_time_hrs: float
    avg_view_percentage: float
    avg_sub_conversion: float
    top_keywords: List[str]
    representative_videos: List[str]
    promoted_to_analytics_group: bool
    silhouette_score: float
    davies_bouldin_index: float

class TrafficSourceItem(BaseModel):
    traffic_source_type: str
    views: int
    watch_time_minutes: float
    view_share_pct: float
    watch_share_pct: float
    retention_efficiency_score: float
    opportunity_score: float
    quadrant: str  # 'Growth Engine', 'Hidden Gem', 'Inefficient Volume', 'Niche'

class DemographicItem(BaseModel):
    dimension_type: str
    dimension_value: str
    playback_group: str
    viewer_percentage: float
    normalized_percentage: float
    is_suppressed: bool
    display_text: str

class PredictionRequest(BaseModel):
    title: str
    duration_sec: int
    cluster_label: str = "Technical Tutorial"
    upload_hour: int = 14
    upload_day_of_week: int = 2
    early_24h_views: Optional[int] = None

class PredictionResponse(BaseModel):
    predicted_30d_views: int
    predicted_watch_time_hrs: float
    predicted_avg_view_percentage: float
    confidence_interval_low: int
    confidence_interval_high: int
    predicted_tier: str
    feature_contributions: Dict[str, float]
    actionable_improvements: List[str]

class NextVideoIdea(BaseModel):
    idea_title: str
    topic_cluster: str
    suggested_format: str
    suggested_duration_range: str
    reason: str
    evidence: Dict[str, Any]
    expected_objective: str
    confidence: str
    potential_risk: str
    priority_score: float

class ABExperimentPlan(BaseModel):
    experiment_id: str
    video_id: Optional[str] = None
    hypothesis: str
    variant_type: str
    control_variant: str
    treatment_variant: str
    metric_targeted: str
    sample_size_control: int
    sample_size_treatment: int
    status: str
    observed_effect_size: Optional[float] = None
    confidence_interval: Optional[str] = None
    outcome_conclusion: Optional[str] = None

class DataQualityReportResponse(BaseModel):
    report_id: str
    quality_score: float
    missingness_summary: Dict[str, Any]
    duplicate_summary: Dict[str, Any]
    anomaly_summary: Dict[str, Any]
    schema_validation_summary: Dict[str, Any]
    generated_at: str

class ChannelGrowthScoreCard(BaseModel):
    reach_score: float
    engagement_score: float
    retention_score: float
    subscriber_growth_score: float
    audience_loyalty_score: float
    content_consistency_score: float
    composite_growth_score: float
    component_weights: Dict[str, float]

class ComplianceStatus(BaseModel):
    raw_video_count: int
    raw_daily_rows: int
    raw_retention_points: int
    derived_metrics_count: int
    retention_policy_default: str
    days_to_earliest_ttl: int
    total_sweeps_performed: int
    last_sweep_timestamp: Optional[str]
    audit_exception_status: str

class QuotaStatus(BaseModel):
    daily_ceiling: int
    units_consumed_today: int
    remaining_units: int
    percentage_used: float
    endpoint_breakdown: Dict[str, int]
    quota_reset_in_hours: int

"""
YouTube Channel Growth Intelligence Platform - Configuration
Contains core parameters, compliance thresholds, and API configuration.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Tuple
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "YouTube Channel Growth Intelligence Platform"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./youtube_growth.db")
    
    # YouTube API & Quota Parameters (Section 2.2)
    DAILY_QUOTA_CEILING: int = 10000
    PROVISIONAL_WINDOW_DAYS: int = 3  # Processing latency window for YouTube Analytics
    REPORTING_JOB_READ_DELAY_HOURS: int = 48
    REPORTING_JOB_BACKFILL_DAYS: int = 30
    
    # Compliance & Data Retention Rule (ToS Section III.E.4.b–d)
    YOUTUBE_DATA_TTL_DAYS: int = 30
    DEFAULT_RETENTION_POLICY: str = "PURGE"  # Pattern B: Derive early, purge raw; or 'REFRESH'
    
    # Statistical & Curve Fitting Parameters
    RETENTION_FIT_R2_MIN: float = 0.70  # Suppress lambda parameter if fit quality R^2 is below 0.70
    MIN_SAMPLE_SIZE_FOR_CLAIM: int = 8  # Minimum sample size before asserting strong recommendations
    LOW_VOLUME_SUPPRESSION_EXPECTED: bool = True
    VIRALITY_ROBUST_Z_THRESHOLD: float = 1.5
    ANALYTICS_GROUP_MAX_ITEMS: int = 500  # API hard limit for custom groups
    
    # Incompatible Metric/Dimension combinations (Confirmed YouTube API constraints)
    # E.g. liveOrOnDemand cannot be combined with averageViewPercentage in channel reports
    INCOMPATIBLE_PAIRS: List[Tuple[str, str]] = [
        ("liveOrOnDemand", "averageViewPercentage"),
        ("isCurated", "*")  # Deprecated dimension
    ]
    
    # JWT & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-jwt-key-growth-intelligence-2026")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

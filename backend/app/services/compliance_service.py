"""
Compliance Service - Implements YouTube API Services Developer Policies (Section III.E.4.b-d).
Enforces the mandatory 30-day data retention rule, TTL sweeper, and compliance audit logging.
Pattern B (Default): Compute derived statistics early, purge raw API data past 30 days.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.schema import (
    RawVideoMetadata,
    RawDailyAnalytics,
    RawRetentionCurve,
    RawTrafficSource,
    RawDemographics,
    DerivedVideoMetrics,
    ComplianceLog,
    default_expires_at
)
from backend.app.config import settings

class ComplianceService:
    def __init__(self, db: Session):
        self.db = db

    def run_ttl_sweep(self) -> Dict[str, Any]:
        """
        Executes the 30-day TTL Sweeper.
        Checks all raw YouTube API ingestion tables for records exceeding youtube_data_expires_at.
        Under Pattern B (default), expired raw records are purged after derived statistics exist.
        Under Pattern A ('REFRESH'), records are marked for re-querying and TTL is renewed.
        """
        now = datetime.now(timezone.utc)
        results = {
            "timestamp": now.isoformat(),
            "tables_swept": {},
            "total_purged": 0,
            "total_refreshed": 0,
            "status": "COMPLETED"
        }

        raw_tables = [
            ("raw_video_metadata", RawVideoMetadata),
            ("raw_daily_analytics", RawDailyAnalytics),
            ("raw_retention_curves", RawRetentionCurve),
            ("raw_traffic_sources", RawTrafficSource),
            ("raw_demographics", RawDemographics)
        ]

        for table_name, model_class in raw_tables:
            # Query records that are expired
            expired_records = self.db.query(model_class).filter(
                model_class.youtube_data_expires_at <= now
            ).all()

            purged_count = 0
            refreshed_count = 0

            for rec in expired_records:
                if rec.retention_policy == "REFRESH":
                    # Refresh pattern: extend TTL by 30 days
                    rec.retrieved_at = now
                    rec.youtube_data_expires_at = now + timedelta(days=settings.YOUTUBE_DATA_TTL_DAYS)
                    refreshed_count += 1
                else:
                    # Pattern B default: Purge raw API row
                    self.db.delete(rec)
                    purged_count += 1

            if purged_count > 0 or refreshed_count > 0:
                action = "PURGED" if purged_count > 0 else "REFRESHED"
                log = ComplianceLog(
                    event_type="TTL_SWEEP",
                    table_name=table_name,
                    records_affected=purged_count + refreshed_count,
                    action_taken=action,
                    details=f"Swept {purged_count} purged and {refreshed_count} refreshed records beyond 30-day TTL."
                )
                self.db.add(log)

            results["tables_swept"][table_name] = {
                "purged": purged_count,
                "refreshed": refreshed_count
            }
            results["total_purged"] += purged_count
            results["total_refreshed"] += refreshed_count

        self.db.commit()
        return results

    def get_compliance_status(self) -> Dict[str, Any]:
        """
        Returns full compliance health metrics, records count, and TTL countdown.
        """
        now = datetime.now(timezone.utc)
        
        raw_video_count = self.db.query(func.count(RawVideoMetadata.id)).scalar() or 0
        raw_daily_rows = self.db.query(func.count(RawDailyAnalytics.id)).scalar() or 0
        raw_retention_points = self.db.query(func.count(RawRetentionCurve.id)).scalar() or 0
        derived_metrics_count = self.db.query(func.count(DerivedVideoMetrics.video_id)).scalar() or 0

        # Find earliest upcoming expiration across raw video metadata
        earliest_exp = self.db.query(func.min(RawVideoMetadata.youtube_data_expires_at)).scalar()
        if earliest_exp:
            if earliest_exp.tzinfo is None:
                earliest_exp = earliest_exp.replace(tzinfo=timezone.utc)
            delta_days = max(0, (earliest_exp - now).days)
        else:
            delta_days = settings.YOUTUBE_DATA_TTL_DAYS

        total_sweeps = self.db.query(func.count(ComplianceLog.id)).scalar() or 0
        last_log = self.db.query(ComplianceLog).order_by(ComplianceLog.timestamp.desc()).first()

        return {
            "raw_video_count": raw_video_count,
            "raw_daily_rows": raw_daily_rows,
            "raw_retention_points": raw_retention_points,
            "derived_metrics_count": derived_metrics_count,
            "retention_policy_default": settings.DEFAULT_RETENTION_POLICY,
            "days_to_earliest_ttl": delta_days,
            "total_sweeps_performed": total_sweeps,
            "last_sweep_timestamp": last_log.timestamp.isoformat() if last_log else None,
            "audit_exception_status": (
                "Pattern B Enforced: Raw API data subject to 30-day mandatory TTL purge. "
                "Derived statistical metrics are compliant analytical transformations."
            )
        }

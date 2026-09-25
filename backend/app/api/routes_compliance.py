"""
Compliance, Data Sources, and Admin API Routes.
Exposes:
1. 30-day Data Retention Rule compliance status and TTL countdowns.
2. Manual and scheduled TTL Sweeper execution (Purge / Refresh).
3. YouTube Data API v3 Quota Ledger tracking against 10,000 daily ceiling.
4. Channel re-seed and ingestion trigger.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone

from backend.app.database import get_db
from backend.app.services.compliance_service import ComplianceService
from backend.app.services.ingestion_service import IngestionService
from backend.app.models.schema import QuotaLedger, ComplianceLog
from backend.app.config import settings

router = APIRouter(tags=["Compliance & Data Sources"])

@router.get("/compliance/status")
def get_compliance_status(db: Session = Depends(get_db)):
    """
    Returns full compliance health metrics, records count, and TTL countdown
    governed by YouTube API Developer Policies Section III.E.4.b-d.
    """
    service = ComplianceService(db)
    return service.get_compliance_status()

@router.post("/compliance/sweep")
def trigger_ttl_sweep(db: Session = Depends(get_db)):
    """
    Triggers the 30-day TTL Sweeper.
    Purges raw YouTube API rows that have exceeded youtube_data_expires_at under Pattern B.
    """
    service = ComplianceService(db)
    return service.run_ttl_sweep()

@router.get("/compliance/logs")
def get_compliance_logs(limit: int = 20, db: Session = Depends(get_db)):
    """Returns recent audit logs of TTL sweeps and compliance events."""
    logs = db.query(ComplianceLog).order_by(ComplianceLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "event_type": l.event_type,
            "table_name": l.table_name,
            "records_affected": l.records_affected,
            "action_taken": l.action_taken,
            "details": l.details,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None
        }
        for l in logs
    ]

@router.get("/quota/status")
def get_quota_status(db: Session = Depends(get_db)):
    """Returns today's YouTube Data API v3 quota consumption vs 10,000 unit ceiling."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    total_cost = db.query(func.sum(QuotaLedger.cost_units)).filter(
        QuotaLedger.timestamp >= today_start
    ).scalar() or 0

    endpoints_raw = db.query(
        QuotaLedger.endpoint,
        func.sum(QuotaLedger.cost_units)
    ).filter(QuotaLedger.timestamp >= today_start).group_by(QuotaLedger.endpoint).all()

    endpoint_map = {ep: int(cost) for ep, cost in endpoints_raw}

    ceiling = settings.DAILY_QUOTA_CEILING
    remaining = max(0, ceiling - total_cost)
    pct = round((total_cost / ceiling) * 100.0, 2)

    return {
        "daily_ceiling": ceiling,
        "units_consumed_today": total_cost,
        "remaining_units": remaining,
        "percentage_used": pct,
        "endpoint_breakdown": endpoint_map,
        "quota_reset_in_hours": 24 - datetime.now(timezone.utc).hour
    }

@router.post("/sync/seed")
def reseed_channel_data(db: Session = Depends(get_db)):
    """Reseeds synthetic channel data with complete historical retention and timeseries."""
    service = IngestionService(db)
    result = service.seed_synthetic_channel("DevPulse Systems")
    return result

"""
Audience Retention API Routes.
Provides retention curves, exponential decay model fits, R^2 gating status,
intro hook drop-off diagnostics, and comparative retention benchmarks.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.app.database import get_db
from backend.app.models.schema import RawRetentionCurve, DerivedVideoMetrics
from backend.app.services.retention_service import RetentionService
from backend.app.config import settings

router = APIRouter(tags=["Retention"])

@router.get("/retention/{video_id}")
def get_video_retention(video_id: str, db: Session = Depends(get_db)):
    """
    Returns full retention curve points, fitted exponential decay model,
    R^2 goodness-of-fit, and lambda suppression flag if R^2 < 0.70.
    """
    video = db.query(DerivedVideoMetrics).filter(DerivedVideoMetrics.video_id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    points = db.query(RawRetentionCurve).filter(
        RawRetentionCurve.video_id == video_id
    ).order_by(RawRetentionCurve.relative_position.asc()).all()

    point_dicts = [
        {
            "second_offset": p.second_offset,
            "relative_position": p.relative_position,
            "retention_percentage": p.retention_percentage
        }
        for p in points
    ]

    fit_res = RetentionService.fit_retention_curve(point_dicts)
    dynamics = RetentionService.analyze_retention_dynamics(point_dicts, video.duration_sec)

    return {
        "video_id": video.video_id,
        "title": video.title,
        "duration_sec": video.duration_sec,
        "points_count": len(points),
        "observed_points": point_dicts,
        "fitted_curve": fit_res.get("fitted_curve", []),
        "retention_decay_lambda": fit_res.get("retention_decay_lambda"),
        "retention_r2": fit_res.get("retention_r2"),
        "is_lambda_suppressed": fit_res.get("is_lambda_suppressed"),
        "fit_status": fit_res.get("fit_status"),
        "r2_threshold": settings.RETENTION_FIT_R2_MIN,
        "suppression_explanation": (
            "Fit quality R^2 is below the 0.70 statistical threshold. "
            "Lambda parameter suppressed to prevent misleading decay assumptions on irregular or re-watched segments."
            if fit_res.get("is_lambda_suppressed") else "Valid exponential decay profile."
        ),
        "intro_dropoff_30s": dynamics.get("intro_dropoff_30s"),
        "mid_video_dips_count": dynamics.get("mid_video_dips_count"),
        "rewatch_spikes_count": dynamics.get("rewatch_spikes_count"),
        "end_screen_rate": dynamics.get("end_screen_rate"),
        "hook_health": dynamics.get("hook_health")
    }

@router.get("/retention-overview")
def get_retention_overview(db: Session = Depends(get_db)):
    """Returns channel-wide hook retention distribution and decay metrics."""
    videos = db.query(DerivedVideoMetrics).all()
    if not videos:
        return {"error": "No videos found"}

    drops = [v.intro_dropoff_30s for v in videos]
    avg_drop = round(sum(drops) / len(drops), 1)
    
    # Categorize hook health
    excellent_hooks = sum(1 for d in drops if d <= 25.0)
    average_hooks = sum(1 for d in drops if 25.0 < d <= 35.0)
    leaky_hooks = sum(1 for d in drops if d > 35.0)

    # Average lambda for videos with valid fits
    valid_lambdas = [v.retention_decay_lambda for v in videos if not v.is_lambda_suppressed and v.retention_decay_lambda is not None]
    avg_lambda = round(sum(valid_lambdas) / len(valid_lambdas), 2) if valid_lambdas else 1.45

    return {
        "channel_avg_intro_drop_30s": avg_drop,
        "excellent_hooks_count": excellent_hooks,
        "average_hooks_count": average_hooks,
        "leaky_hooks_count": leaky_hooks,
        "avg_decay_lambda": avg_lambda,
        "suppressed_fits_count": sum(1 for v in videos if v.is_lambda_suppressed)
    }

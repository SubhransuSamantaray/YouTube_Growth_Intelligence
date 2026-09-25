"""
Reports API Routes.
Provides PDF download, HTML view, and CSV export of executive growth reports.
Supports Brutal Analysis toggle.
"""
from fastapi import APIRouter, Depends, Query, Response, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
import os

from backend.app.database import get_db
from backend.app.models.schema import DerivedVideoMetrics, Recommendation, DerivedContentCluster
from backend.app.services.report_service import ReportService

router = APIRouter(tags=["Reports"])

@router.get("/reports/pdf")
def download_pdf_report(
    is_brutal: bool = Query(False, description="Toggle Brutal Analysis report format"),
    db: Session = Depends(get_db)
):
    """Generates and streams an executive PDF growth report."""
    videos = db.query(DerivedVideoMetrics).order_by(DerivedVideoMetrics.total_views.desc()).all()
    if not videos:
        raise HTTPException(status_code=400, detail="No video data available for report generation.")

    video_dicts = [
        {
            "video_id": v.video_id,
            "title": v.title,
            "format_type": v.format_type,
            "total_views": v.total_views,
            "total_watch_time_hrs": v.total_watch_time_hrs,
            "avg_view_percentage": v.avg_view_percentage,
            "virality_robust_z": v.virality_robust_z,
            "performance_tier": v.performance_tier,
            "intro_dropoff_30s": v.intro_dropoff_30s,
            "sub_conversion_per_1k": v.sub_conversion_per_1k,
            "engagement_rate": v.engagement_rate
        }
        for v in videos
    ]

    total_views = sum(v["total_views"] for v in video_dicts)
    total_watch = round(sum(v["total_watch_time_hrs"] for v in video_dicts), 1)
    total_subs = sum(v.net_subscribers for v in videos)
    avg_duration = sum(v.avg_view_duration_sec for v in videos) / len(videos)
    avg_pct = sum(v.avg_view_percentage for v in videos) / len(videos)
    avg_eng = sum(v.engagement_rate for v in videos) / len(videos)
    viral_count = sum(1 for v in videos if v.performance_tier == "Viral Breakout")

    summary = {
        "total_videos": len(videos),
        "total_views": total_views,
        "total_watch_time_hrs": total_watch,
        "total_subscribers": total_subs,
        "avg_view_duration_sec": avg_duration,
        "avg_view_percentage": avg_pct,
        "avg_engagement_rate": avg_eng,
        "viral_videos_count": viral_count,
        "top_format": "Deep Dive",
        "avg_intro_drop": round(sum(v["intro_dropoff_30s"] for v in video_dicts) / len(video_dicts), 1)
    }

    recs = db.query(Recommendation).filter(Recommendation.is_brutal == is_brutal).order_by(
        Recommendation.priority_score.desc()
    ).all()
    rec_dicts = [
        {
            "rec_id": r.rec_id,
            "category": r.category,
            "title": r.title,
            "recommendation_text": r.recommendation_text,
            "priority_score": r.priority_score,
            "impact_score": r.impact_score,
            "effort_score": r.effort_score,
            "evidence_object": r.evidence_object
        }
        for r in recs
    ]

    clusters = db.query(DerivedContentCluster).all()
    cluster_dicts = [{"cluster_name": c.cluster_name, "video_count": c.video_count} for c in clusters]

    pdf_filename = f"reports_generated/Executive_Growth_Report_{'Brutal' if is_brutal else 'Standard'}.pdf"
    ReportService.generate_pdf_report(
        channel_name="DevPulse Systems",
        channel_summary=summary,
        top_videos=video_dicts,
        recommendations=rec_dicts,
        clusters=cluster_dicts,
        output_filepath=pdf_filename,
        is_brutal=is_brutal
    )

    return FileResponse(
        pdf_filename,
        media_type="application/pdf",
        filename=os.path.basename(pdf_filename)
    )

@router.get("/reports/html", response_class=HTMLResponse)
def view_html_report(
    is_brutal: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Renders a standalone executive HTML report with print stylesheets."""
    videos = db.query(DerivedVideoMetrics).order_by(DerivedVideoMetrics.total_views.desc()).all()
    video_dicts = [
        {
            "video_id": v.video_id,
            "title": v.title,
            "format_type": v.format_type,
            "total_views": v.total_views,
            "total_watch_time_hrs": v.total_watch_time_hrs,
            "avg_view_percentage": v.avg_view_percentage,
            "virality_robust_z": v.virality_robust_z,
            "performance_tier": v.performance_tier
        }
        for v in videos
    ]

    total_views = sum(v["total_views"] for v in video_dicts)
    total_watch = round(sum(v["total_watch_time_hrs"] for v in video_dicts), 1)
    total_subs = sum(v.net_subscribers for v in videos)
    avg_duration = sum(v.avg_view_duration_sec for v in videos) / len(videos) if videos else 0
    avg_pct = sum(v.avg_view_percentage for v in videos) / len(videos) if videos else 0

    summary = {
        "total_videos": len(videos),
        "total_views": total_views,
        "total_watch_time_hrs": total_watch,
        "total_subscribers": total_subs,
        "avg_view_duration_sec": avg_duration,
        "avg_view_percentage": avg_pct
    }

    recs = db.query(Recommendation).filter(Recommendation.is_brutal == is_brutal).order_by(
        Recommendation.priority_score.desc()
    ).all()
    rec_dicts = [
        {
            "category": r.category,
            "title": r.title,
            "recommendation_text": r.recommendation_text,
            "priority_score": r.priority_score,
            "impact_score": r.impact_score,
            "effort_score": r.effort_score,
            "evidence_object": r.evidence_object
        }
        for r in recs
    ]

    html_content = ReportService.generate_html_report(
        channel_name="DevPulse Systems",
        channel_summary=summary,
        top_videos=video_dicts,
        recommendations=rec_dicts,
        clusters=[],
        is_brutal=is_brutal
    )

    return HTMLResponse(content=html_content)

@router.get("/reports/csv")
def download_csv_export(db: Session = Depends(get_db)):
    """Exports video performance records to CSV."""
    videos = db.query(DerivedVideoMetrics).all()
    video_dicts = [
        {
            "video_id": v.video_id,
            "title": v.title,
            "published_at": v.published_at.isoformat() if v.published_at else "",
            "duration_sec": v.duration_sec,
            "format_type": v.format_type,
            "total_views": v.total_views,
            "total_watch_time_hrs": v.total_watch_time_hrs,
            "avg_view_percentage": v.avg_view_percentage,
            "virality_robust_z": v.virality_robust_z,
            "performance_tier": v.performance_tier,
            "sub_conversion_per_1k": v.sub_conversion_per_1k,
            "engagement_rate": v.engagement_rate,
            "intro_dropoff_30s": v.intro_dropoff_30s
        }
        for v in videos
    ]

    csv_data = ReportService.export_videos_csv(video_dicts)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=youtube_channel_growth_data.csv"}
    )

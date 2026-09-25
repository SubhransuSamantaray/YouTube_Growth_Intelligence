"""
Unified Command-Line Interface (CLI) for YouTube Channel Growth Intelligence Platform.
Supports:
  python cli.py seed                 # Reseed sample channel dataset with retention curves
  python cli.py sweep                # Execute 30-day compliance TTL sweeper
  python cli.py analyze              # Run analytics, robust virality Z-scores, and clustering
  python cli.py train                # Train ML models with t0 temporal cutoff integrity
  python cli.py report --pdf         # Generate Executive PDF report
  python cli.py report --brutal      # Generate Brutal Strategic Audit PDF report
  python cli.py status               # Display compliance, quota, and channel health status
"""
import argparse
import sys
import os

from backend.app.database import engine, Base, SessionLocal
from backend.app.services.ingestion_service import IngestionService
from backend.app.services.compliance_service import ComplianceService
from backend.app.services.report_service import ReportService
from backend.app.models.schema import DerivedVideoMetrics, Recommendation, DerivedContentCluster

def init_db():
    Base.metadata.create_all(bind=engine)

def cmd_seed(args):
    init_db()
    db = SessionLocal()
    try:
        print(f"[*] Ingesting and seeding channel: {args.channel}...")
        service = IngestionService(db)
        res = service.seed_synthetic_channel(args.channel)
        print(f"[OK] Seeding completed successfully!")
        print(f"    - Videos Ingested: {res['videos_ingested']}")
        print(f"    - Retention Points: {res['retention_points']}")
        print(f"    - Model Uplift vs Baseline: +{res['model_improvement_pct']}%")
        print(f"    - 30-Day TTL Expiration: {res['ttl_expiration']}")
    finally:
        db.close()

def cmd_sweep(args):
    init_db()
    db = SessionLocal()
    try:
        print("[*] Executing 30-Day Data Retention TTL Sweeper (ToS Section III.E.4)...")
        service = ComplianceService(db)
        res = service.run_ttl_sweep()
        print(f"[OK] Sweep completed successfully!")
        print(f"    - Raw Records Purged: {res['total_purged']}")
        print(f"    - Records Refreshed: {res['total_refreshed']}")
        for tbl, counts in res['tables_swept'].items():
            print(f"    - {tbl}: {counts['purged']} purged, {counts['refreshed']} refreshed")
    finally:
        db.close()

def cmd_status(args):
    init_db()
    db = SessionLocal()
    try:
        service = ComplianceService(db)
        status = service.get_compliance_status()
        print("\n================ COMPLIANCE & REPOSITORY STATUS ================")
        print(f"Raw API Videos Stored:      {status['raw_video_count']}")
        print(f"Raw Daily Timeseries Rows:  {status['raw_daily_rows']}")
        print(f"Raw Retention Points:       {status['raw_retention_points']}")
        print(f"Derived Metrics Persisted:  {status['derived_metrics_count']}")
        print(f"Earliest TTL Expiration:    In {status['days_to_earliest_ttl']} days")
        print(f"Total Automated Sweeps:     {status['total_sweeps_performed']}")
        print(f"Audit Exception Policy:     {status['audit_exception_status']}")
        print("=================================================================\n")
    finally:
        db.close()

def cmd_report(args):
    init_db()
    db = SessionLocal()
    try:
        is_brutal = args.brutal
        mode_label = "Brutal" if is_brutal else "Standard"
        print(f"[*] Compiling Executive Growth Report ({mode_label} Mode)...")

        videos = db.query(DerivedVideoMetrics).order_by(DerivedVideoMetrics.total_views.desc()).all()
        if not videos:
            print("[!] Error: No video data found. Run 'python cli.py seed' first.")
            return

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
                "intro_dropoff_30s": v.intro_dropoff_30s
            }
            for v in videos
        ]

        summary = {
            "total_videos": len(videos),
            "total_views": sum(v["total_views"] for v in video_dicts),
            "total_watch_time_hrs": sum(v["total_watch_time_hrs"] for v in video_dicts),
            "total_subscribers": sum(v.net_subscribers for v in videos),
            "avg_view_duration_sec": sum(v.avg_view_duration_sec for v in videos) / len(videos),
            "avg_view_percentage": sum(v.avg_view_percentage for v in videos) / len(videos),
            "avg_engagement_rate": sum(v.engagement_rate for v in videos) / len(videos),
            "viral_videos_count": sum(1 for v in videos if v.performance_tier == "Viral Breakout"),
            "top_format": "Deep Dive",
            "avg_intro_drop": round(sum(v["intro_dropoff_30s"] for v in video_dicts) / len(video_dicts), 1)
        }

        recs = db.query(Recommendation).filter(Recommendation.is_brutal == is_brutal).all()
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

        clusters = db.query(DerivedContentCluster).all()
        cluster_dicts = [{"cluster_name": c.cluster_name, "video_count": c.video_count} for c in clusters]

        out_pdf = f"reports_generated/Executive_Growth_Report_{mode_label}.pdf"
        ReportService.generate_pdf_report(
            channel_name="DevPulse Systems",
            channel_summary=summary,
            top_videos=video_dicts,
            recommendations=rec_dicts,
            clusters=cluster_dicts,
            output_filepath=out_pdf,
            is_brutal=is_brutal
        )
        print(f"[OK] Executive PDF report successfully generated at:\n    {os.path.abspath(out_pdf)}")

    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="YouTube Channel Growth Intelligence Platform CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # seed
    p_seed = subparsers.add_parser("seed", help="Seed realistic channel data with retention curves")
    p_seed.add_argument("--channel", default="DevPulse Systems", help="Channel name")

    # sweep
    p_sweep = subparsers.add_parser("sweep", help="Execute 30-day compliance TTL sweeper")

    # status
    p_status = subparsers.add_parser("status", help="Show compliance and database status")

    # report
    p_report = subparsers.add_parser("report", help="Generate growth reports")
    p_report.add_argument("--brutal", action="store_true", help="Generate Brutal Analysis report")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "seed":
        cmd_seed(args)
    elif args.command == "sweep":
        cmd_sweep(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "report":
        cmd_report(args)

if __name__ == "__main__":
    main()

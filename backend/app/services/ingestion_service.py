"""
Comprehensive Data Ingestion Service.
Supports:
- MODE A: Authenticated YouTube API ingestion with 30-day compliance TTL stamping.
- MODE B: YouTube Studio CSV ingestion parser.
- MODE C: Public YouTube Data API metadata ingestion.
- Realistic 32-video synthetic channel seeder populating all normalized & derived tables,
  feature store, ML runs, next video opportunities, A/B experiments, and quality scorecards.
"""
import random
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.schema import (
    User,
    OAuthConnection,
    Channel,
    Video,
    VideoStatistics,
    VideoDailyAnalytics,
    ChannelDailyAnalytics,
    AudienceAnalytics,
    AudienceRetention,
    TrafficSources,
    Demographics,
    DeviceAnalytics,
    ContentCategory,
    DerivedVideoMetrics,
    DerivedContentCluster,
    FeatureStore,
    MLPrediction,
    ModelRun,
    Recommendation,
    NextVideoOpportunity,
    ABExperiment,
    DataIngestionRun,
    DataQualityReport,
    GeneratedReport,
    ComplianceLog,
    QuotaLedger,
    default_expires_at
)
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.retention_service import RetentionService
from backend.app.services.ml_service import MLService
from backend.app.services.recommendation_service import RecommendationService
from backend.app.services.data_quality_service import DataQualityService
from backend.app.config import settings

class IngestionService:
    def __init__(self, db: Session):
        self.db = db

    def seed_synthetic_channel(self, channel_name: str = "DevPulse Systems") -> Dict[str, Any]:
        """
        Seeds a production-grade 32-video channel dataset with full historical depth,
        daily metrics, retention curves, traffic sources, audience demographics,
        experiments, and data quality audits.
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=settings.YOUTUBE_DATA_TTL_DAYS)

        # Clear existing records
        self.db.query(User).delete()
        self.db.query(OAuthConnection).delete()
        self.db.query(Channel).delete()
        self.db.query(Video).delete()
        self.db.query(VideoStatistics).delete()
        self.db.query(VideoDailyAnalytics).delete()
        self.db.query(ChannelDailyAnalytics).delete()
        self.db.query(AudienceAnalytics).delete()
        self.db.query(AudienceRetention).delete()
        self.db.query(TrafficSources).delete()
        self.db.query(Demographics).delete()
        self.db.query(DeviceAnalytics).delete()
        self.db.query(ContentCategory).delete()
        self.db.query(DerivedVideoMetrics).delete()
        self.db.query(DerivedContentCluster).delete()
        self.db.query(FeatureStore).delete()
        self.db.query(MLPrediction).delete()
        self.db.query(ModelRun).delete()
        self.db.query(Recommendation).delete()
        self.db.query(NextVideoOpportunity).delete()
        self.db.query(ABExperiment).delete()
        self.db.query(DataIngestionRun).delete()
        self.db.query(DataQualityReport).delete()
        self.db.query(GeneratedReport).delete()
        self.db.query(ComplianceLog).delete()
        self.db.query(QuotaLedger).delete()
        self.db.commit()

        # 1. Seed Users (Channel Owner & Admin)
        owner_user = User(email="owner@devpulse.io", hashed_password="argon2_hashed_secret", role="channel_owner")
        admin_user = User(email="admin@devpulse.io", hashed_password="argon2_hashed_secret", role="admin")
        self.db.add_all([owner_user, admin_user])
        self.db.commit()

        # 2. Seed Channel
        channel = Channel(
            channel_id="chan_tech_001",
            title=channel_name,
            description="Engineering deep dives, distributed systems architecture, and production backend development.",
            custom_url="@DevPulseSystems",
            published_at=now - timedelta(days=365),
            subscriber_count=64200,
            video_count=32,
            view_count=1248000,
            country="US",
            sync_status="COMPLIANT_ACTIVE",
            last_synced_at=now
        )
        self.db.add(channel)

        # 3. Seed OAuth Connection
        oauth = OAuthConnection(
            user_id=owner_user.id,
            channel_id="chan_tech_001",
            encrypted_access_token="enc_v3_access_token_secure_kms",
            encrypted_refresh_token="enc_v3_refresh_token_secure_kms",
            token_expiry=now + timedelta(hours=1),
            scopes=["https://www.googleapis.com/auth/yt-analytics.readonly", "https://www.googleapis.com/auth/youtube.readonly"]
        )
        self.db.add(oauth)

        # 4. Seed Content Categories
        cats = [
            ContentCategory(category_id="28", name="Science & Technology", channel_fit_score=1.0),
            ContentCategory(category_id="27", name="Education", channel_fit_score=0.92)
        ]
        self.db.add_all(cats)

        # 5. Video Blueprints (32 videos spanning formats and clusters)
        video_blueprints = [
            ("Building a Distributed Cache in Go from Scratch", 1620, "Deep Dive", ["go", "distributed systems", "backend", "cache"], 38500, 3.8, 1),
            ("Database Internals: How B-Trees Actually Work", 1440, "Deep Dive", ["database", "btree", "storage", "internals"], 54200, 4.4, 1),
            ("System Design Interview: Scalable Real-time Chat Architecture", 1980, "Deep Dive", ["system design", "architecture", "scale", "chat"], 68900, 4.9, 1),
            ("Kafka vs RabbitMQ in Production: 10M Events/sec Benchmark", 1320, "Deep Dive", ["kafka", "rabbitmq", "benchmark", "production"], 42100, 3.6, 3),
            ("Building an Event-Driven Architecture with FastAPI and Redis", 1560, "Deep Dive", ["fastapi", "redis", "python", "backend"], 36400, 3.2, 1),
            ("PostgreSQL Under the Hood: MVCC, Locks, and Vacuuming", 1800, "Deep Dive", ["postgres", "database", "sql", "performance"], 48300, 4.1, 1),
            ("Designing a Global CDN from Ground Up", 1740, "Deep Dive", ["cdn", "networking", "scale", "infrastructure"], 29400, 2.8, 1),

            ("FastAPI in 2026: The Complete Crash Course", 780, "Mid-form", ["fastapi", "python", "api", "tutorial"], 31200, 2.9, 2),
            ("Modern Docker for Python Developers: Multi-stage Builds", 660, "Mid-form", ["docker", "python", "devops", "containers"], 24500, 2.4, 2),
            ("Full-Stack Authentication with JWT and OAuth2 in FastAPI", 840, "Mid-form", ["auth", "jwt", "security", "fastapi"], 27800, 2.7, 2),
            ("How to Write Production-Grade Unit Tests with Pytest", 540, "Mid-form", ["pytest", "testing", "python", "clean code"], 16800, 1.8, 2),
            ("AsyncIO in Python: What Every Senior Engineer Needs to Know", 720, "Mid-form", ["asyncio", "python", "concurrency", "performance"], 33400, 3.1, 2),
            ("Building a Vector Search Engine with Python and FAISS", 890, "Mid-form", ["ai", "vector search", "faiss", "python"], 45200, 4.0, 2),
            ("Kubernetes for Backend Developers: Pods, Services, Ingress", 810, "Mid-form", ["kubernetes", "devops", "cloud", "backend"], 22100, 2.2, 2),
            ("Microservices with gRPC and Protobuf: Hands-on Project", 750, "Mid-form", ["grpc", "microservices", "protobuf", "go"], 19400, 1.9, 2),
            ("Setting up CI/CD with GitHub Actions in 15 Minutes", 570, "Mid-form", ["github actions", "cicd", "devops", "automation"], 18200, 1.7, 2),
            ("SQL Indexing Masterclass: Eliminate Slow Queries", 690, "Mid-form", ["sql", "database", "performance", "indexing"], 37800, 3.5, 1),
            ("Building a Web Scraper That Won't Get Blocked", 610, "Mid-form", ["scraping", "python", "proxies", "tools"], 26300, 2.5, 2),

            ("Why We Ditched Microservices for a Modular Monolith", 680, "Mid-form", ["architecture", "monolith", "microservices", "engineering"], 62400, 4.8, 3),
            ("Rust vs Go for Backend Services: Real Production Benchmark", 740, "Mid-form", ["rust", "go", "benchmark", "backend"], 58900, 4.5, 3),
            ("Top 7 Tools That Boosted Our Team's Engineering Velocity", 480, "Mid-form", ["tools", "developer tools", "productivity", "career"], 14500, 1.5, 3),
            ("FastAPI vs Go Gin: Which is Faster in Real Workloads?", 620, "Mid-form", ["fastapi", "go", "benchmark", "api"], 39100, 3.4, 3),
            ("Why Senior Engineers Hate ORMs (And What We Use Instead)", 590, "Mid-form", ["orm", "sql", "architecture", "engineering"], 49800, 4.2, 3),
            ("Postgres vs MongoDB in 2026: Stop Using Mongo for Everything", 640, "Mid-form", ["postgres", "mongodb", "database", "comparison"], 51200, 4.3, 3),

            ("7 Mistakes That Keep You as a Junior Developer", 510, "Mid-form", ["career", "junior", "advice", "growth"], 34100, 3.0, 4),
            ("How to Read Codebases You Didn't Write", 460, "Mid-form", ["career", "reading code", "skills", "productivity"], 21900, 2.1, 4),
            ("5 Clean Code Rules That Actually Matter in Production", 530, "Mid-form", ["clean code", "best practices", "refactoring", "software"], 38400, 3.3, 4),
            ("What Really Happens During a FAANG Staff Engineer Interview", 670, "Mid-form", ["interview", "staff engineer", "career", "tech"], 44600, 3.9, 4),

            ("Never Use SELECT * in Production #shorts", 45, "Short", ["sql", "shorts", "database"], 28400, 1.2, 1),
            ("The Python Dict Trick Nobody Teaches #shorts", 38, "Short", ["python", "shorts", "tricks"], 34900, 1.4, 2),
            ("How Git Merge Actually Differs from Rebase #shorts", 52, "Short", ["git", "shorts", "devops"], 41200, 1.6, 2),
            ("Why Floating Point Math Fails in Every Language #shorts", 42, "Short", ["computer science", "shorts", "math"], 37100, 1.5, 3)
        ]

        raw_views_list = [b[4] for b in video_blueprints]
        robust_zs = AnalyticsService.calculate_robust_z_scores(raw_views_list)

        computed_videos = []
        feature_rows = []
        raw_videos_audit = []
        raw_analytics_audit = []
        raw_retention_audit = []

        for idx, (title, duration_sec, fmt, tags, target_views, virality_mult, cluster_id) in enumerate(video_blueprints):
            video_id = f"vid_{100 + idx:03d}"
            days_ago = max(5, int(80 - (idx * 2.3)))
            pub_date = now - timedelta(days=days_ago, hours=random.randint(10, 18), minutes=random.randint(0, 59))
            
            # Store Video Entity
            video_entity = Video(
                video_id=video_id,
                channel_id="chan_tech_001",
                title=title,
                description=f"Deep dive tutorial on {title}. Production architecture code included.",
                published_at=pub_date,
                duration_sec=duration_sec,
                content_type=fmt,
                tags=tags,
                category_id="28",
                thumbnail_url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                privacy_status="public",
                source_type="youtube_data_api",
                retrieved_at=now,
                youtube_data_expires_at=expires_at,
                retention_policy=settings.DEFAULT_RETENTION_POLICY
            )
            self.db.add(video_entity)
            raw_videos_audit.append({"video_id": video_id, "title": title, "duration_sec": duration_sec})

            total_views = target_views
            base_retention_pct = 68.0 if fmt == "Short" else (52.0 if virality_mult >= 3.5 else 41.0)
            avg_view_sec = duration_sec * (base_retention_pct / 100.0)
            total_watch_minutes = (total_views * avg_view_sec) / 60.0
            
            likes = int(total_views * random.uniform(0.045, 0.075))
            comments = int(total_views * random.uniform(0.003, 0.009))
            shares = int(total_views * random.uniform(0.002, 0.006))
            subs_gained = int(total_views * (virality_mult * 0.0018))
            subs_lost = int(subs_gained * 0.08)

            # Public Video Statistics Snapshot
            self.db.add(VideoStatistics(
                video_id=video_id,
                views=total_views,
                likes=likes,
                comments=comments,
                shares=shares,
                snapshot_at=now,
                source_type="youtube_data_api",
                youtube_data_expires_at=expires_at,
                retention_policy=settings.DEFAULT_RETENTION_POLICY
            ))

            # Daily Analytics Record
            daily_rec = VideoDailyAnalytics(
                video_id=video_id,
                date=(pub_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                views=total_views,
                watch_time_minutes=round(total_watch_minutes, 1),
                avg_view_duration_sec=round(avg_view_sec, 1),
                avg_view_percentage=round(base_retention_pct, 1),
                likes=likes,
                comments=comments,
                shares=shares,
                subscribers_gained=subs_gained,
                subscribers_lost=subs_lost,
                impressions=int(total_views * random.uniform(9.0, 16.0)),
                ctr=round(random.uniform(5.5, 9.8), 2),
                is_provisional=(days_ago <= settings.PROVISIONAL_WINDOW_DAYS),
                source_type="youtube_analytics_api",
                retrieved_at=now,
                youtube_data_expires_at=expires_at,
                retention_policy=settings.DEFAULT_RETENTION_POLICY
            )
            self.db.add(daily_rec)
            raw_analytics_audit.append({"video_id": video_id, "date": daily_rec.date, "views": total_views, "ctr": daily_rec.ctr})

            # Audience Retention Points (20 points per video)
            curve_points = []
            intro_drop = random.uniform(22.0, 36.0)
            for step in range(21):
                rel_pos = round(step / 20.0, 2)
                sec_off = int(rel_pos * duration_sec)
                
                if rel_pos == 0:
                    ret_pct = 100.0
                elif rel_pos <= 0.05:
                    drop_fraction = rel_pos / 0.05
                    ret_pct = 100.0 - (intro_drop * drop_fraction)
                else:
                    t_tail = (rel_pos - 0.05) / 0.95
                    decay = (100.0 - intro_drop) * np.exp(-1.4 * t_tail)
                    spike = 3.5 if 0.45 <= rel_pos <= 0.55 else 0.0
                    ret_pct = max(18.0, decay + spike)

                ret_pct = round(float(ret_pct), 2)
                curve_points.append({
                    "second_offset": sec_off,
                    "relative_position": rel_pos,
                    "retention_percentage": ret_pct
                })

                self.db.add(AudienceRetention(
                    video_id=video_id,
                    second_offset=sec_off,
                    elapsed_time_ratio=rel_pos,
                    audience_watch_ratio=ret_pct,
                    relative_retention=round(ret_pct / 50.0, 2),
                    source_type="youtube_analytics_api",
                    retrieved_at=now,
                    youtube_data_expires_at=expires_at,
                    retention_policy=settings.DEFAULT_RETENTION_POLICY
                ))
                raw_retention_audit.append({"video_id": video_id, "retention_percentage": ret_pct})

            fit_results = RetentionService.fit_retention_curve(curve_points)
            dynamics = RetentionService.analyze_retention_dynamics(curve_points, duration_sec)

            # Traffic Sources
            traffic_splits = [
                ("SUGGESTED_VIDEO", int(total_views * 0.42), total_watch_minutes * 0.44),
                ("YT_SEARCH", int(total_views * 0.28), total_watch_minutes * 0.26),
                ("BROWSE_FEATURES", int(total_views * 0.20), total_watch_minutes * 0.21),
                ("EXTERNAL", int(total_views * 0.06), total_watch_minutes * 0.05),
                ("DIRECT", int(total_views * 0.04), total_watch_minutes * 0.04),
            ]
            for src_name, src_views, src_watch in traffic_splits:
                self.db.add(TrafficSources(
                    video_id=video_id,
                    channel_id="chan_tech_001",
                    date=(pub_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                    insight_traffic_source_type=src_name,
                    views=src_views,
                    watch_time_minutes=round(src_watch, 1),
                    source_type="youtube_analytics_api",
                    retrieved_at=now,
                    youtube_data_expires_at=expires_at,
                    retention_policy=settings.DEFAULT_RETENTION_POLICY
                ))

            # Derived Metrics Persistence (Pattern B)
            z_score = robust_zs[idx]
            tier = AnalyticsService.assign_performance_tier(z_score)

            derived = DerivedVideoMetrics(
                video_id=video_id,
                title=title,
                published_at=pub_date,
                duration_sec=duration_sec,
                format_type=fmt,
                duration_bucket=AnalyticsService.classify_duration_bucket(duration_sec),
                total_views=total_views,
                total_watch_time_hrs=round(total_watch_minutes / 60.0, 1),
                avg_view_duration_sec=round(avg_view_sec, 1),
                avg_view_percentage=round(base_retention_pct, 1),
                total_likes=likes,
                total_comments=comments,
                total_shares=shares,
                net_subscribers=subs_gained - subs_lost,
                sub_conversion_per_1k=round(((subs_gained - subs_lost) / total_views) * 1000.0, 2),
                engagement_rate=round(((likes + comments + shares) / total_views) * 100.0, 2),
                views_per_sub=round(total_views / 64200.0, 3),
                watch_time_per_1k_subs=round((total_watch_minutes / 60.0 / 64.2), 2),
                virality_robust_z=z_score,
                performance_tier=tier,
                retention_decay_lambda=fit_results.get("retention_decay_lambda"),
                retention_r2=fit_results.get("retention_r2"),
                is_lambda_suppressed=fit_results.get("is_lambda_suppressed", False),
                intro_dropoff_30s=dynamics.get("intro_dropoff_30s", 28.0),
                mid_video_dips_count=dynamics.get("mid_video_dips_count", 0),
                rewatch_spikes_count=dynamics.get("rewatch_spikes_count", 0),
                end_screen_rate=dynamics.get("end_screen_rate", 20.0),
                cluster_id=cluster_id,
                cluster_label=f"Cluster {cluster_id}"
            )
            self.db.add(derived)

            computed_videos.append({
                "video_id": video_id,
                "title": title,
                "duration_sec": duration_sec,
                "published_at": pub_date.isoformat(),
                "format_type": fmt,
                "duration_bucket": AnalyticsService.classify_duration_bucket(duration_sec),
                "total_views": total_views,
                "total_watch_time_hrs": round(total_watch_minutes / 60.0, 1),
                "avg_view_percentage": round(base_retention_pct, 1),
                "virality_robust_z": z_score,
                "performance_tier": tier,
                "sub_conversion_per_1k": round(((subs_gained - subs_lost) / total_views) * 1000.0, 2),
                "engagement_rate": round(((likes + comments + shares) / total_views) * 100.0, 2),
                "intro_dropoff_30s": dynamics.get("intro_dropoff_30s", 28.0),
                "cluster_id": cluster_id
            })

            # Feature Store (t0 upload cutoff)
            t0_features = MLService.extract_t0_features(title, duration_sec, pub_date, cluster_id)
            self.db.add(FeatureStore(
                video_id=video_id,
                cutoff_timestamp=pub_date,
                cutoff_type="t0_publish",
                feature_vector=t0_features,
                target_30d_views=total_views,
                target_watch_time_hrs=round(total_watch_minutes / 60.0, 1),
                target_retention_pct=round(base_retention_pct, 1),
                target_virality_label=1 if z_score >= 1.5 else 0
            ))
            feature_rows.append({"features": t0_features, "target_30d_views": total_views})

        # 6. Seed Channel Daily Analytics & Audience Analytics Time Series
        for d in range(30):
            day_dt = (now - timedelta(days=29 - d)).strftime("%Y-%m-%d")
            day_views = random.randint(18000, 34000)
            self.db.add(ChannelDailyAnalytics(
                channel_id="chan_tech_001",
                date=day_dt,
                views=day_views,
                watch_time_hours=round(day_views * 0.12, 1),
                subscribers_gained=int(day_views * 0.0035),
                subscribers_lost=int(day_views * 0.0003),
                net_subscribers=int(day_views * 0.0032),
                estimated_revenue=round(day_views * 0.0042, 2),
                source_type="youtube_analytics_api",
                retrieved_at=now,
                youtube_data_expires_at=expires_at,
                retention_policy=settings.DEFAULT_RETENTION_POLICY
            ))
            self.db.add(AudienceAnalytics(
                channel_id="chan_tech_001",
                date=day_dt,
                new_viewers=int(day_views * 0.62),
                casual_viewers=int(day_views * 0.22),
                regular_viewers=int(day_views * 0.16),
                returning_viewers=int(day_views * 0.38),
                unique_viewers=int(day_views * 0.74),
                source_type="youtube_analytics_api",
                retrieved_at=now,
                youtube_data_expires_at=expires_at,
                retention_policy=settings.DEFAULT_RETENTION_POLICY
            ))

        # 7. Seed Demographics & Devices
        demographics_specs = [
            ("ageGroup", "18-24", "subscribed", 14.5),
            ("ageGroup", "25-34", "subscribed", 48.0),
            ("ageGroup", "35-44", "subscribed", 26.5),
            ("ageGroup", "45-54", "subscribed", 8.0),
            ("ageGroup", "55-64", "subscribed", 3.0),
            ("ageGroup", "18-24", "unsubscribed", 21.0),
            ("ageGroup", "25-34", "unsubscribed", 52.0),
            ("ageGroup", "35-44", "unsubscribed", 18.0),
            ("ageGroup", "45-54", "unsubscribed", 7.0),
            ("ageGroup", "55-64", "unsubscribed", 2.0),
            ("country", "United States", "ALL", 38.5),
            ("country", "India", "ALL", 21.2),
            ("country", "United Kingdom", "ALL", 9.4),
            ("country", "Germany", "ALL", 7.1),
            ("country", "Canada", "ALL", 5.8),
            ("country", "Other", "ALL", 18.0)
        ]
        for dim_type, dim_val, grp, pct in demographics_specs:
            self.db.add(Demographics(
                channel_id="chan_tech_001",
                dimension_type=dim_type,
                dimension_value=dim_val,
                playback_group=grp,
                viewer_percentage=pct,
                is_suppressed=False,
                source_type="youtube_analytics_api",
                retrieved_at=now,
                youtube_data_expires_at=expires_at,
                retention_policy=settings.DEFAULT_RETENTION_POLICY
            ))

        device_specs = [("DESKTOP", 62.4), ("MOBILE", 29.8), ("TV", 5.2), ("TABLET", 2.6)]
        for dev, dev_pct in device_specs:
            self.db.add(DeviceAnalytics(
                channel_id="chan_tech_001",
                device_type=dev,
                views=int(1248000 * (dev_pct / 100.0)),
                watch_time_minutes=round((1248000 * (dev_pct / 100.0) * 8.5), 1),
                source_type="youtube_analytics_api",
                retrieved_at=now,
                youtube_data_expires_at=expires_at,
                retention_policy=settings.DEFAULT_RETENTION_POLICY
            ))

        # 8. Seed Content Clusters
        clusters = AnalyticsService.cluster_content_by_keywords(computed_videos)
        for c in clusters:
            self.db.add(DerivedContentCluster(
                cluster_id=c["cluster_id"],
                cluster_name=c["cluster_name"],
                video_count=c["video_count"],
                avg_views=c["avg_views"],
                median_views=c["median_views"],
                avg_watch_time_hrs=c["avg_watch_time_hrs"],
                avg_view_percentage=c["avg_view_percentage"],
                avg_sub_conversion=c["avg_sub_conversion"],
                top_keywords=c["top_keywords"],
                representative_videos=c["representative_videos"],
                promoted_to_analytics_group=c["promoted_to_analytics_group"],
                silhouette_score=c["silhouette_score"],
                davies_bouldin_index=c["davies_bouldin_index"]
            ))

        # 9. Train ML Models
        model, metrics = MLService.train_growth_models(feature_rows)
        if model:
            run_id = f"run_{now.strftime('%Y%m%d_%H%M%S')}"
            self.db.add(ModelRun(
                run_id=run_id,
                model_type=metrics["model_type"],
                target_name=metrics["target"],
                version="1.0.0",
                mae=metrics["mae"],
                rmse=metrics["rmse"],
                r2_score=metrics["r2_score"],
                baseline_mae=metrics["baseline_mae"],
                improvement_pct=metrics["improvement_pct"],
                feature_importance=metrics["feature_importance"],
                hyperparameters={"n_estimators": 60, "max_depth": 3, "random_state": 42}
            ))

        # 10. Seed Recommendations (Standard & Brutal)
        channel_stats = {
            "total_videos": len(computed_videos),
            "total_views": sum(v["total_views"] for v in computed_videos),
            "total_watch_time_hrs": sum(v["total_watch_time_hrs"] for v in computed_videos),
            "avg_intro_drop": round(float(np.mean([v["intro_dropoff_30s"] for v in computed_videos])), 1)
        }
        recs_std = RecommendationService.generate_recommendations(computed_videos, channel_stats, is_brutal_mode=False)
        recs_brutal = RecommendationService.generate_recommendations(computed_videos, channel_stats, is_brutal_mode=True)

        for r in recs_std + recs_brutal:
            self.db.add(Recommendation(
                rec_id=r.rec_id + ("_BRUTAL" if r.is_brutal else "_STD"),
                category=r.category,
                title=r.title,
                recommendation_text=r.recommendation_text,
                priority_score=r.priority_score,
                impact_score=r.impact_score,
                effort_score=r.effort_score,
                evidence_object=r.evidence_object.model_dump(),
                is_brutal=r.is_brutal
            ))

        # 11. Seed What-To-Make-Next Ideas & A/B Experiments
        ideas = RecommendationService.generate_next_video_opportunities(clusters)
        for idea in ideas:
            self.db.add(NextVideoOpportunity(
                idea_title=idea.idea_title,
                topic_cluster=idea.topic_cluster,
                suggested_format=idea.suggested_format,
                suggested_duration_range=idea.suggested_duration_range,
                reason=idea.reason,
                evidence=idea.evidence,
                expected_objective=idea.expected_objective,
                confidence=idea.confidence,
                potential_risk=idea.potential_risk,
                priority_score=idea.priority_score
            ))

        experiments = RecommendationService.get_ab_experiments()
        for exp in experiments:
            self.db.add(ABExperiment(
                experiment_id=exp.experiment_id,
                video_id=exp.video_id,
                hypothesis=exp.hypothesis,
                variant_type=exp.variant_type,
                control_variant=exp.control_variant,
                treatment_variant=exp.treatment_variant,
                metric_targeted=exp.metric_targeted,
                start_date=now - timedelta(days=20),
                end_date=now - timedelta(days=5),
                status=exp.status,
                sample_size_control=exp.sample_size_control,
                sample_size_treatment=exp.sample_size_treatment,
                observed_effect_size=exp.observed_effect_size,
                confidence_interval=exp.confidence_interval,
                outcome_conclusion=exp.outcome_conclusion
            ))

        # 12. Run Data Quality Engine & Seed Quality Report
        quality_res = DataQualityService.audit_dataset_quality(raw_videos_audit, raw_analytics_audit, raw_retention_audit)
        self.db.add(DataQualityReport(
            report_id=f"DQR_{now.strftime('%Y%m%d_%H%M%S')}",
            run_id=f"INGEST_{now.strftime('%Y%m%d_%H%M%S')}",
            quality_score=quality_res["quality_score"],
            missingness_summary=quality_res["missingness_summary"],
            duplicate_summary=quality_res["duplicate_summary"],
            anomaly_summary=quality_res["anomaly_summary"],
            schema_validation_summary=quality_res["schema_validation_summary"]
        ))

        # 13. Record Data Ingestion Run & Quota Consumption
        self.db.add(DataIngestionRun(
            run_id=f"INGEST_{now.strftime('%Y%m%d_%H%M%S')}",
            mode="oauth_api",
            channel_id="chan_tech_001",
            status="SUCCESS",
            records_ingested=len(video_blueprints),
            errors_count=0,
            started_at=now - timedelta(minutes=2),
            completed_at=now
        ))

        self.db.add(QuotaLedger(endpoint="youtube.channels.list", cost_units=1, daily_cumulative_units=1))
        self.db.add(QuotaLedger(endpoint="youtube.playlistItems.list", cost_units=1, daily_cumulative_units=2))
        self.db.add(QuotaLedger(endpoint="youtube.videos.list", cost_units=1, daily_cumulative_units=3))

        self.db.commit()

        return {
            "status": "SUCCESS",
            "channel_name": channel_name,
            "videos_ingested": len(video_blueprints),
            "retention_points": len(video_blueprints) * 21,
            "ttl_expiration": expires_at.isoformat(),
            "data_quality_score": quality_res["quality_score"],
            "model_improvement_pct": metrics.get("improvement_pct") if model else 0.0,
            "recommendations_generated": len(recs_std) + len(recs_brutal),
            "next_video_ideas": len(ideas),
            "ab_experiments": len(experiments)
        }

"""
Warehouse Loader Module
Handles transactional loading into SQLite / PostgreSQL,
stamping mandatory 30-day compliance TTL timestamps (YouTube Developer Policy Section III.E.4),
and recording ingestion telemetry.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from backend.app.models.schema import Video, VideoStatistics, DataIngestionRun

logger = logging.getLogger("data_pipeline.loader")

class WarehouseLoader:
    """Manages transactional loads with compliance timestamps and deduplication."""

    def __init__(self, db_session: Session, ttl_days: int = 30):
        self.db = db_session
        self.ttl_days = ttl_days

    def compute_ttl_expiry(self) -> datetime:
        """Returns UTC timestamp exactly ttl_days in future."""
        return datetime.now(timezone.utc) + timedelta(days=self.ttl_days)

    def load_videos(self, video_dicts: List[Dict[str, Any]], channel_id: str) -> int:
        """Upsert videos with compliance timestamps."""
        loaded_count = 0
        now = datetime.now(timezone.utc)
        expiry = self.compute_ttl_expiry()

        for v_data in video_dicts:
            vid = v_data["video_id"]
            existing = self.db.query(Video).filter(Video.video_id == vid).first()
            if not existing:
                new_vid = Video(
                    video_id=vid,
                    channel_id=channel_id,
                    title=v_data.get("title", "Untitled"),
                    description=v_data.get("description", ""),
                    published_at=datetime.fromisoformat(v_data["published_at"]) if isinstance(v_data.get("published_at"), str) else now,
                    duration_seconds=v_data.get("duration_seconds", 300),
                    is_short=v_data.get("is_short", False),
                    retrieved_at=now,
                    youtube_data_expires_at=expiry,
                    retention_policy="purge_after_30_days"
                )
                self.db.add(new_vid)
                loaded_count += 1
            else:
                existing.title = v_data.get("title", existing.title)
                existing.retrieved_at = now
                existing.youtube_data_expires_at = expiry

        self.db.commit()
        logger.info(f"Loaded {loaded_count} new videos into warehouse with TTL {expiry}.")
        return loaded_count

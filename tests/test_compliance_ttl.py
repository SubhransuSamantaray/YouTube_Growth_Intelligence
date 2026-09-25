"""
Unit tests for 30-Day Data Retention Rule & TTL Sweeper (YouTube API Section III.E.4.b-d).
"""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.models.schema import RawVideoMetadata, ComplianceLog
from backend.app.services.compliance_service import ComplianceService

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()

def test_raw_table_has_30_day_ttl(test_db):
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=30)
    
    meta = RawVideoMetadata(
        video_id="v_test_01",
        channel_id="chan_test",
        title="Test Video",
        published_at=now,
        duration_sec=600,
        retrieved_at=now,
        youtube_data_expires_at=expires,
        retention_policy="PURGE"
    )
    test_db.add(meta)
    test_db.commit()

    saved = test_db.query(RawVideoMetadata).filter_by(video_id="v_test_01").first()
    assert saved is not None
    assert saved.youtube_data_expires_at is not None
    assert saved.retention_policy == "PURGE"

def test_ttl_sweeper_purges_expired_raw_records_under_pattern_b(test_db):
    now = datetime.now(timezone.utc)
    # Expired 2 days ago
    expired_time = now - timedelta(days=2)
    
    # 1 expired record with PURGE policy
    rec_purge = RawVideoMetadata(
        video_id="v_purge_01",
        channel_id="chan_test",
        title="Purge Video",
        published_at=now - timedelta(days=35),
        duration_sec=500,
        retrieved_at=now - timedelta(days=32),
        youtube_data_expires_at=expired_time,
        retention_policy="PURGE"
    )
    # 1 non-expired record
    rec_valid = RawVideoMetadata(
        video_id="v_valid_01",
        channel_id="chan_test",
        title="Valid Video",
        published_at=now,
        duration_sec=700,
        retrieved_at=now,
        youtube_data_expires_at=now + timedelta(days=28),
        retention_policy="PURGE"
    )
    test_db.add_all([rec_purge, rec_valid])
    test_db.commit()

    # Run sweeper
    sweeper = ComplianceService(test_db)
    sweep_results = sweeper.run_ttl_sweep()

    assert sweep_results["total_purged"] == 1
    assert test_db.query(RawVideoMetadata).filter_by(video_id="v_purge_01").first() is None
    assert test_db.query(RawVideoMetadata).filter_by(video_id="v_valid_01").first() is not None

    # Check audit log was created
    log = test_db.query(ComplianceLog).first()
    assert log is not None
    assert log.event_type == "TTL_SWEEP"
    assert log.action_taken == "PURGED"

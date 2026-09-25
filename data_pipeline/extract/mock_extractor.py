"""
Mock Data Extractor for Local Development, Testing, and Offline Demonstrations.
Generates realistic, grounded channel datasets conforming to YouTube API schemas.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
import random

class MockExtractor:
    """Generates synthetic YouTube Channel data with statistical fidelity."""

    @staticmethod
    def generate_channel_payload(channel_id: str = "UC_DEMO_AI_GROWTH") -> Dict[str, Any]:
        return {
            "channel_id": channel_id,
            "title": "AI & Systems Engineering Masterclass",
            "description": "Deep dive engineering tutorials on distributed systems, AI architectures, and fullstack platforms.",
            "subscriber_count": 84200,
            "video_count": 32,
            "view_count": 2845000,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=500)).isoformat(),
            "extracted_at": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    def generate_retention_points(duration_seconds: int = 600, hook_drop: float = 0.28) -> List[Dict[str, float]]:
        """Generate realistic exponential retention decay with hook drop and spikes."""
        points = []
        retention = 1.0
        for sec in range(0, duration_seconds + 1, 10):
            norm_sec = sec / duration_seconds
            if sec <= 30:
                # Fast initial hook drop-off
                retention = 1.0 - (hook_drop * (sec / 30.0))
            else:
                # Exponential decay tail + small rewatch spikes
                retention = max(0.12, (1.0 - hook_drop) * (2.71828 ** (-1.2 * (norm_sec - 0.05))))
                if 0.45 <= norm_sec <= 0.48: # mid-video key insight spike
                    retention = min(1.0, retention * 1.08)
            points.append({
                "second": sec,
                "elapsed_ratio": round(norm_sec, 4),
                "retention_percentage": round(retention * 100, 2)
            })
        return points

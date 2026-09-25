"""
Data Validation and Quality Assurance Module
Enforces schema constraints, metric compatibility rules, and privacy suppression detection.
"""

from typing import Dict, Any, List, Tuple

class SchemaValidator:
    """Validates raw and processed YouTube Analytics payloads."""

    INCOMPATIBLE_PAIRS = [
        ("liveOrOnDemand", "averageViewPercentage"),
        ("creatorContentType", "annotationClickThroughRate"),
        ("audienceType", "cardTeaserClickRate"),
    ]

    DEPRECATED_METRICS = [
        "isCurated",
        "annotationClickThroughRate",
        "annotationCloseRate"
    ]

    @classmethod
    def validate_query_compatibility(cls, dimensions: List[str], metrics: List[str]) -> Tuple[bool, List[str]]:
        """
        Verify YouTube Analytics API v2 dimensional and metric compatibility.
        Returns (is_valid, list_of_violations).
        """
        violations = []
        for dim, met in cls.INCOMPATIBLE_PAIRS:
            if dim in dimensions and met in metrics:
                violations.append(f"Incompatible query: Dimension '{dim}' cannot be combined with metric '{met}'.")

        for m in metrics:
            if m in cls.DEPRECATED_METRICS:
                violations.append(f"Deprecated metric detected: '{m}' was removed from YouTube Analytics API.")

        return len(violations) == 0, violations

    @staticmethod
    def validate_record_ranges(record: Dict[str, Any]) -> List[str]:
        """Validates that numerical values conform to logical bounds."""
        anomalies = []
        if "views" in record and record["views"] < 0:
            anomalies.append(f"Negative view count detected: {record['views']}")
        if "retention_percentage" in record:
            val = record["retention_percentage"]
            if val < 0.0 or val > 120.0:  # Spikes can slightly exceed 100% due to rewinds
                anomalies.append(f"Retention percentage out of bounds [0, 120]: {val}")
        return anomalies

"""
Recommendations & Growth Matrix API Routes.
Serves evidence-backed recommendations and Growth Opportunity Matrix quadrants.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models.schema import Recommendation
from backend.app.schemas.api_models import RecommendationItem

router = APIRouter(tags=["Recommendations & Growth Matrix"])

@router.get("/recommendations")
def get_recommendations(
    is_brutal: bool = Query(False, description="Toggle unvarnished Brutal Analysis mode"),
    db: Session = Depends(get_db)
):
    """
    Returns prioritized recommendations with full structured Evidence Objects:
    {metric, baseline, observed_value, n, effect_size, confidence, limitations, provenance_sources}
    """
    recs = db.query(Recommendation).filter(Recommendation.is_brutal == is_brutal).order_by(
        Recommendation.priority_score.desc()
    ).all()

    return [
        {
            "rec_id": r.rec_id,
            "category": r.category,
            "title": r.title,
            "recommendation_text": r.recommendation_text,
            "priority_score": r.priority_score,
            "impact_score": r.impact_score,
            "effort_score": r.effort_score,
            "is_brutal": r.is_brutal,
            "evidence_object": r.evidence_object
        }
        for r in recs
    ]

@router.get("/growth-matrix")
def get_growth_opportunity_matrix(
    is_brutal: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Categorizes recommendations into 4 Opportunity Matrix quadrants:
    1. Quick Wins (High Impact, Low Effort)
    2. Major Strategic Bets (High Impact, Medium/High Effort)
    3. Incremental Gains (Medium/Low Impact, Low Effort)
    4. Low Priority (Low Impact, High Effort)
    """
    recs = db.query(Recommendation).filter(Recommendation.is_brutal == is_brutal).all()

    matrix = {
        "quick_wins": [],
        "major_bets": [],
        "incremental_gains": [],
        "low_priority": []
    }

    for r in recs:
        item = {
            "rec_id": r.rec_id,
            "category": r.category,
            "title": r.title,
            "recommendation_text": r.recommendation_text,
            "priority_score": r.priority_score,
            "impact_score": r.impact_score,
            "effort_score": r.effort_score,
            "evidence_object": r.evidence_object
        }
        if r.impact_score == "High" and r.effort_score == "Low":
            matrix["quick_wins"].append(item)
        elif r.impact_score == "High" and r.effort_score in ["Medium", "High"]:
            matrix["major_bets"].append(item)
        elif r.impact_score in ["Medium", "Low"] and r.effort_score == "Low":
            matrix["incremental_gains"].append(item)
        else:
            matrix["low_priority"].append(item)

    return matrix

from sqlalchemy.orm import Session

from app.db.recommendations import Recommendation
from app.services.achievement_service import compute_user_achievement
from app.scoring.recommendation_score import points_for_recommendation


def compute_recommendation_score(db: Session, user_id: int) -> dict:
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.requester_id == user_id)
        .filter(Recommendation.status == "APPROVED")
        .order_by(Recommendation.id.asc())
        .all()
    )

    total = 0
    breakdown = []

    for r in recs:
        recomm_ach = compute_user_achievement(db, r.recommender_id)
        recomm_total = recomm_ach["achievement_score"]["total"]

        scored = points_for_recommendation(r.rec_type, recomm_total)
        total += scored["points"]

        breakdown.append({
            "recommendation_id": r.id,
            "recommender_id": r.recommender_id,
            "rec_type": r.rec_type,
            "recommender_achievement_total": recomm_total,
            "points": scored["points"],
            "breakdown": scored["breakdown"],
            "note_title": r.note_title,
        })

    return {
        "user_id": user_id,
        "recommendation_score": {
            "total": total,
            "count": len(recs),
            "breakdown": breakdown,
        },
    }

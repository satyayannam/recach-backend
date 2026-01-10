from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.recommendations import Recommendation
from app.db.models import User
from app.api.achievement import get_user_achievement  # reuse your function
from app.scoring.recommendation_score import points_for_recommendation

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}/recommendation-score")
def get_recommendation_score(user_id: int, db: Session = Depends(get_db)):
    # all approved recs received by this user
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
        # compute recommender achievement total (reuse existing endpoint logic)
        recomm_ach = get_user_achievement(r.recommender_id, db)
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

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models import User
from app.db.user_profile import UserProfile
from app.api.achievement import get_user_achievement
from app.api.recommendation_score import get_recommendation_score


def search_public_users(db: Session, q: str, limit: int = 10):
    q_like = f"%{q.strip()}%"

    rows = (
        db.query(User, UserProfile)
        .join(UserProfile, UserProfile.user_id == User.id)
        .filter(UserProfile.visibility == "PUBLIC")
        .filter(
            or_(
                UserProfile.full_name.ilike(q_like),
                UserProfile.headline.ilike(q_like),
                UserProfile.location.ilike(q_like),
            )
        )
        .limit(limit)
        .all()
    )

    out = []
    for user, profile in rows:
        ach = get_user_achievement(user.id, db)
        rec = get_recommendation_score(user.id, db)

        out.append({
            "user_id": user.id,
            "full_name": profile.full_name,
            "headline": profile.headline,
            "location": profile.location,
            "interests": profile.interests,
            "visibility": profile.visibility,
            "achievement_score": ach["achievement_score"]["total"],
            "recommendation_score": rec["recommendation_score"]["total"],
        })

    return out

# app/services/public_user.py
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.user_profile import UserProfile
from app.api.achievement import get_user_achievement
from app.api.recommendation_score import get_recommendation_score


def _totals(db: Session, user_id: int) -> tuple[int, int]:
    # achievement total
    ach = get_user_achievement(user_id, db)
    achievement_total = ach["achievement_score"]["total"]

    # recommendation total
    rec = get_recommendation_score(user_id, db)
    recommendation_total = rec["recommendation_score"]["total"]

    return achievement_total, recommendation_total


def search_public_users(db: Session, q: str, limit: int = 10):
    users = (
        db.query(User)
        .filter(User.status == "APPROVED")
        .filter(User.full_name.ilike(f"%{q}%"))
        .limit(limit)
        .all()
    )

    results = []
    for u in users:
        profile = db.query(UserProfile).filter(UserProfile.user_id == u.id).first()
        achievement_total, recommendation_total = _totals(db, u.id)

        results.append({
            "user_id": u.id,
            "full_name": u.full_name,
            "username": u.username,
            "headline": getattr(profile, "headline", None) if profile else None,
            "achievement_total": achievement_total,
            "recommendation_total": recommendation_total,
            "profile_photo_url": getattr(profile, "profile_photo_url", None) if profile else None,
        })

    return results


def get_public_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.status != "APPROVED":
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    achievement_total, recommendation_total = _totals(db, user_id)

    interests = []
    if hasattr(profile, "interests") and profile.interests:
        if isinstance(profile.interests, list):
            interests = profile.interests
        else:
            interests = [x.strip() for x in str(profile.interests).split(",") if x.strip()]

    return {
        "user_id": user.id,
        "full_name": user.full_name,
        "headline": getattr(profile, "headline", None),
        "bio": getattr(profile, "bio", None),
        "location": getattr(profile, "location", None),
        "interests": interests,
        "achievement_total": achievement_total,
        "recommendation_total": recommendation_total,
    }

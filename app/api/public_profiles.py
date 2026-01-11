# app/api/public_profiles.py

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.deps import get_db
from app.db.models import User
from app.db.recommendations import Recommendation
from app.db.user_profile import UserProfile
from app.services.public_user import search_public_users
from app.services.username import normalize_username
from app.api.public_profile_schemas import (
    PublicUserSearchOut,
    PublicUserOut,
    RecommenderMini,
)

router = APIRouter(prefix="/public/users", tags=["Public Users"])


@router.get("/search", response_model=List[PublicUserSearchOut])
def search_users(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return search_public_users(db, q, limit)


# ✅ username-based public profile
@router.get("/{username}", response_model=PublicUserOut)
def public_user_by_username(username: str, db: Session = Depends(get_db)):
    # normalize '^satya' -> 'satya'
    try:
        uname = normalize_username(username)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid username")

    user = db.query(User).filter(User.username == uname).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Build base public profile payload (minimal + safe)
    # If you already have a "get_public_user" service, you can call it with user.id,
    # but this version stays independent and won't break if the service expects id.
    base = {
        "id": user.id,
        "full_name": user.full_name,
        "username": user.username,
    }

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    base["profile_photo_url"] = profile.profile_photo_url if profile else None

    # Pull approved recommenders
    recs = (
        db.query(User.full_name, User.username)
        .join(Recommendation, Recommendation.recommender_id == User.id)
        .filter(
            Recommendation.requester_id == user.id,
            Recommendation.status == "APPROVED",
        )
        .order_by(
            Recommendation.decided_at.desc().nullslast(),
            Recommendation.created_at.desc(),
        )
        .all()
    )

    base["recommended_by"] = [
        RecommenderMini(full_name=name, username=u) for (name, u) in recs
    ]
    base["recommender_count"] = len(recs)

    return base

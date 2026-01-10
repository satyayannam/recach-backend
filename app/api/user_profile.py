from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.user_profile import UserProfile
from app.api.user_profile_schemas import UserProfileOut, UserProfileUpdate
from app.api.deps_auth import get_current_user

router = APIRouter(prefix="/me/profile", tags=["User Profile"])


@router.get("", response_model=UserProfileOut)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("", response_model=UserProfileOut)
def upsert_my_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    data = payload.model_dump(exclude_unset=True)

    if profile is None:
        profile = UserProfile(user_id=current_user.id, **data)
        db.add(profile)
    else:
        for k, v in data.items():
            setattr(profile, k, v)

    db.commit()
    db.refresh(profile)
    return profile

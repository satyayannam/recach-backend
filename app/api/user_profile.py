import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.user_profile import UserProfile
from app.db.models import User
from app.services.username import normalize_username
from app.api.user_profile_schemas import UserProfileOut, UserProfileUpdate
from app.api.deps_auth import get_current_user

router = APIRouter(prefix="/me/profile", tags=["User Profile"])
MAX_PHOTO_BYTES = 2 * 1024 * 1024
PHOTO_DIR = os.path.join(os.getcwd(), "uploads", "profile_photos")


@router.get("", response_model=UserProfileOut)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    payload = UserProfileOut.model_validate(profile).model_dump()
    payload["username"] = current_user.username
    payload["email"] = current_user.email
    payload["full_name"] = current_user.full_name
    return payload


@router.put("", response_model=UserProfileOut)
def upsert_my_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    data = payload.model_dump(exclude_unset=True)
    username_value = data.pop("username", None)

    if username_value:
        try:
            normalized = normalize_username(username_value)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        existing = db.query(User).filter(User.username == normalized).first()
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=409, detail="Username already taken")
        current_user.username = normalized

    if profile is None:
        profile = UserProfile(user_id=current_user.id, **data)
        db.add(profile)
    else:
        for k, v in data.items():
            setattr(profile, k, v)

    db.commit()
    db.refresh(profile)
    payload = UserProfileOut.model_validate(profile).model_dump()
    payload["username"] = current_user.username
    payload["email"] = current_user.email
    payload["full_name"] = current_user.full_name
    return payload


@router.put("/photo", response_model=UserProfileOut)
async def update_profile_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type")

    content = await file.read()
    if len(content) > MAX_PHOTO_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large")

    ext_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    ext = ext_map.get(file.content_type, ".jpg")

    os.makedirs(PHOTO_DIR, exist_ok=True)
    filename = f"user_{current_user.id}{ext}"
    file_path = os.path.join(PHOTO_DIR, filename)

    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if profile is None:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    if profile.profile_photo_url:
        old_name = os.path.basename(profile.profile_photo_url)
        old_path = os.path.join(PHOTO_DIR, old_name)
        if old_path != file_path and os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass

    with open(file_path, "wb") as out_file:
        out_file.write(content)

    profile.profile_photo_url = f"/media/profile_photos/{filename}"
    db.commit()
    db.refresh(profile)
    return profile

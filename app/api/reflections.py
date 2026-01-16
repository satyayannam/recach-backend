from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps_auth import get_current_user
from app.api.reflection_schemas import ReflectionCreate, ReflectionOut, ReflectionUserOut
from app.db.deps import get_db
from app.db.models import User
from app.db.reflection import Reflection
from app.db.user_profile import UserProfile

router = APIRouter(prefix="/reflections", tags=["Reflections"])

ALLOWED_TYPES = {
    "story"
}


def build_user_out(user: User, profile: UserProfile | None) -> ReflectionUserOut:
    university = None
    if profile and isinstance(profile.university_names, list) and profile.university_names:
        university = str(profile.university_names[0])
    return ReflectionUserOut(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        university=university
    )


@router.post("", response_model=ReflectionOut, status_code=status.HTTP_201_CREATED)
def create_reflection(
    payload: ReflectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid reflection type")
    if not payload.content or len(payload.content.strip()) < 20:
        raise HTTPException(status_code=400, detail="Content must be at least 20 characters")

    reflection = Reflection(
        user_id=current_user.id,
        type=payload.type,
        content=payload.content.strip()
    )
    db.add(reflection)
    db.commit()
    db.refresh(reflection)

    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    )
    return ReflectionOut(
        id=reflection.id,
        type=reflection.type,
        content=reflection.content,
        created_at=reflection.created_at,
        user=build_user_out(current_user, profile)
    )


@router.get("", response_model=list[ReflectionOut])
def list_reflections(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    reflections = (
        db.query(Reflection)
        .order_by(desc(Reflection.created_at))
        .limit(limit)
        .all()
    )

    user_ids = {r.user_id for r in reflections}
    users = (
        db.query(User).filter(User.id.in_(user_ids)).all()
        if user_ids else []
    )
    profiles = (
        db.query(UserProfile).filter(UserProfile.user_id.in_(user_ids)).all()
        if user_ids else []
    )
    user_map = {user.id: user for user in users}
    profile_map = {profile.user_id: profile for profile in profiles}
    output: list[ReflectionOut] = []
    for reflection in reflections:
        user = user_map.get(reflection.user_id)
        if not user:
            continue
        output.append(
            ReflectionOut(
                id=reflection.id,
                type=reflection.type,
                content=reflection.content,
                created_at=reflection.created_at,
                user=build_user_out(user, profile_map.get(user.id))
            )
        )
    return output


@router.get("/{reflection_id}", response_model=ReflectionOut)
def get_reflection(
    reflection_id: int,
    db: Session = Depends(get_db),
):
    reflection = db.query(Reflection).filter(Reflection.id == reflection_id).first()
    if not reflection:
        raise HTTPException(status_code=404, detail="Reflection not found")
    user = db.query(User).filter(User.id == reflection.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    return ReflectionOut(
        id=reflection.id,
        type=reflection.type,
        content=reflection.content,
        created_at=reflection.created_at,
        user=build_user_out(user, profile)
    )

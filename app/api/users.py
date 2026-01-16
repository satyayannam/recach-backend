from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.approval import is_auto_approved_email
from app.core.security import hash_password
from app.db.deps import get_db
from app.db.models import User
from app.api.schemas import UserCreate, UserOut
from app.services.username import normalize_username
from app.services.scores import get_achievement_total, get_recommendation_total
from sqlalchemy import func
from app.db.post import Post
from app.db.post_caret import PostCaret
from app.api.deps_auth import get_current_user


router = APIRouter(prefix="/users", tags=["users"])




@router.get("/me/achievement")
def get_my_achievement_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = get_achievement_total(db, current_user.id)
    return {"user_id": current_user.id, "achievement_score": total}


@router.get("/me/recommendation-score")
def get_my_recommendation_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = get_recommendation_total(db, current_user.id)
    return {"user_id": current_user.id, "recommendation_score": total}


@router.get("/me/reflection-caret-score")
def get_my_reflection_caret_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = (
        db.query(func.count(PostCaret.id))
        .join(Post, Post.id == PostCaret.post_id)
        .filter(Post.user_id == current_user.id)
        .scalar()
        or 0
    )
    return {"user_id": current_user.id, "caret_score": int(total)}

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    # -----------------------------
    # Email uniqueness check
    # -----------------------------
    email = payload.email.strip().lower()
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # -----------------------------
    # Username normalization + check
    # Accepts "^satya" or "satya"
    # -----------------------------
    try:
        username = normalize_username(payload.username)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    existing_username = db.query(User).filter(User.username == username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    # -----------------------------
    # Password hashing
    # -----------------------------
    try:
        hashed = hash_password(payload.password)
    except ValueError as e:
        # bcrypt 72-byte limit protection
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    # -----------------------------
    # Create user
    # -----------------------------
    user = User(
        full_name=payload.full_name.strip(),
        email=email,
        username=username,
        hashed_password=hashed,
    )

    # -----------------------------
    # Auto-approval logic
    # -----------------------------
    if is_auto_approved_email(email):
        user.status = "APPROVED"
        user.approved_at = datetime.utcnow()

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

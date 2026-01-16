from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.api.deps_auth import get_current_user
from app.api.post_schemas import PostCaretOut, PostCreate, PostOut, PostUserOut
from app.db.deps import get_db
from app.db.models import User
from app.db.post import Post
from app.db.post_caret import PostCaret
from app.db.user_profile import UserProfile

router = APIRouter(prefix="/posts", tags=["Posts"])

ALLOWED_TYPES = {
    "behind_resume",
    "this_lately",
    "recent_realization",
    "currently_building"
}


def build_user_out(user: User, profile: UserProfile | None) -> PostUserOut:
    university = None
    if profile and isinstance(profile.university_names, list) and profile.university_names:
        university = str(profile.university_names[0])
    return PostUserOut(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        university=university
    )


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid post type")
    if not payload.content or len(payload.content.strip()) < 20:
        raise HTTPException(status_code=400, detail="Content must be at least 20 characters")

    post = Post(
        user_id=current_user.id,
        type=payload.type,
        content=payload.content.strip()
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    )
    return PostOut(
        id=post.id,
        type=post.type,
        content=post.content,
        created_at=post.created_at,
        user=build_user_out(current_user, profile),
        caret_count=0
    )


@router.get("", response_model=list[PostOut])
def list_posts(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    posts = (
        db.query(Post)
        .order_by(desc(Post.created_at))
        .limit(limit)
        .all()
    )

    user_ids = {p.user_id for p in posts}
    post_ids = [p.id for p in posts]
    users = (
        db.query(User).filter(User.id.in_(user_ids)).all()
        if user_ids else []
    )
    profiles = (
        db.query(UserProfile).filter(UserProfile.user_id.in_(user_ids)).all()
        if user_ids else []
    )
    caret_counts = (
        db.query(PostCaret.post_id, func.count(PostCaret.id))
        .filter(PostCaret.post_id.in_(post_ids))
        .group_by(PostCaret.post_id)
        .all()
        if post_ids else []
    )
    user_map = {user.id: user for user in users}
    profile_map = {profile.user_id: profile for profile in profiles}
    caret_map = {post_id: count for post_id, count in caret_counts}

    output: list[PostOut] = []
    for post in posts:
        user = user_map.get(post.user_id)
        if not user:
            continue
        output.append(
            PostOut(
                id=post.id,
                type=post.type,
                content=post.content,
                created_at=post.created_at,
                user=build_user_out(user, profile_map.get(user.id)),
                caret_count=int(caret_map.get(post.id, 0))
            )
        )
    return output


@router.get("/{post_id}", response_model=PostOut)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    user = db.query(User).filter(User.id == post.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    caret_count = (
        db.query(func.count(PostCaret.id))
        .filter(PostCaret.post_id == post.id)
        .scalar()
        or 0
    )
    return PostOut(
        id=post.id,
        type=post.type,
        content=post.content,
        created_at=post.created_at,
        user=build_user_out(user, profile),
        caret_count=int(caret_count)
    )


@router.put("/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    payload: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to edit this post")
    if payload.type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid post type")
    if not payload.content or len(payload.content.strip()) < 20:
        raise HTTPException(status_code=400, detail="Content must be at least 20 characters")

    post.type = payload.type
    post.content = payload.content.strip()
    db.commit()
    db.refresh(post)

    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    )
    caret_count = (
        db.query(func.count(PostCaret.id))
        .filter(PostCaret.post_id == post.id)
        .scalar()
        or 0
    )
    return PostOut(
        id=post.id,
        type=post.type,
        content=post.content,
        created_at=post.created_at,
        user=build_user_out(current_user, profile),
        caret_count=int(caret_count)
    )


@router.post("/{post_id}/caret", response_model=PostCaretOut)
def toggle_post_caret(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot add caret to your own post")

    existing = (
        db.query(PostCaret)
        .filter(PostCaret.post_id == post_id, PostCaret.user_id == current_user.id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        has_caret = False
    else:
        db.add(PostCaret(post_id=post_id, user_id=current_user.id))
        db.commit()
        has_caret = True

    caret_count = (
        db.query(func.count(PostCaret.id))
        .filter(PostCaret.post_id == post_id)
        .scalar()
        or 0
    )
    return PostCaretOut(
        post_id=post_id,
        caret_count=int(caret_count),
        has_caret=has_caret
    )


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this post")

    db.query(PostCaret).filter(PostCaret.post_id == post_id).delete()
    db.delete(post)
    db.commit()
    return {"status": "deleted"}

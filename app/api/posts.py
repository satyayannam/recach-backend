from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.api.deps_auth import get_current_user, get_optional_user
from app.api.post_schemas import PostCaretOut, PostCreate, PostOut, PostUserOut
from app.api.post_reply_schemas import PostReplyCreate, PostReplyOut
from app.db.deps import get_db
from app.db.inbox_item import InboxItem
from app.db.models import User
from app.db.post import Post
from app.db.post_caret import PostCaret
from app.db.post_reply import PostReply
from app.db.post_reply_caret import PostReplyCaret
from app.db.post_reply_owner_reaction import PostReplyOwnerReaction
from app.db.user_profile import UserProfile
from app.services.permissions import ensure_post_owner

router = APIRouter(prefix="/posts", tags=["Posts"])

ALLOWED_TYPES = {
    "behind_resume",
    "this_lately",
    "recent_realization",
    "currently_building"
}

ALLOWED_REPLY_TYPES = {"validate", "context", "impact", "clarify", "challenge"}


def build_user_out(user: User, profile: UserProfile | None) -> PostUserOut:
    university = None
    if profile and isinstance(profile.university_names, list) and profile.university_names:
        university = str(profile.university_names[0])
    return PostUserOut(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        university=university,
        profile_photo_url=profile.profile_photo_url if profile else None
    )


def build_reply_user_out(user: User, profile: UserProfile | None):
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "profile_photo_url": profile.profile_photo_url if profile else None,
    }


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
        caret_count=0,
        has_caret=False
    )


@router.get("", response_model=list[PostOut])
def list_posts(
    limit: int = Query(50, ge=1, le=200),
    user_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    query = db.query(Post)
    if user_id is not None:
        query = query.filter(Post.user_id == user_id)
    posts = (
        query.order_by(desc(Post.created_at))
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
    user_carets = set()
    if current_user and post_ids:
        user_carets = {
            post_id
            for (post_id,) in db.query(PostCaret.post_id)
            .filter(
                PostCaret.user_id == current_user.id,
                PostCaret.post_id.in_(post_ids),
            )
            .all()
        }
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
                caret_count=int(caret_map.get(post.id, 0)),
                has_caret=post.id in user_carets
            )
        )
    return output


@router.get("/{post_id}", response_model=PostOut)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
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
    has_caret = False
    if current_user:
        has_caret = (
            db.query(PostCaret)
            .filter(
                PostCaret.post_id == post.id,
                PostCaret.user_id == current_user.id,
            )
            .first()
            is not None
        )
    return PostOut(
        id=post.id,
        type=post.type,
        content=post.content,
        created_at=post.created_at,
        user=build_user_out(user, profile),
        caret_count=int(caret_count),
        has_caret=has_caret
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
        caret_count=int(caret_count),
        has_caret=False
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


@router.post("/{post_id}/replies", response_model=PostReplyOut, status_code=status.HTTP_201_CREATED)
def create_post_reply(
    post_id: int,
    payload: PostReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if payload.type not in ALLOWED_REPLY_TYPES:
        raise HTTPException(status_code=400, detail="Invalid reply type")

    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Reply message is required")

    if post.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot reply to your own post")

    recipient_id = post.user_id
    recipient = db.query(User).filter(User.id == recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    reply = PostReply(
        post_id=post.id,
        owner_id=post.user_id,
        sender_id=current_user.id,
        recipient_id=recipient_id,
        type=payload.type,
        message=message,
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)

    sender_profile = (
        db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    )
    post_snippet = post.content.strip()
    if len(post_snippet) > 160:
        post_snippet = f"{post_snippet[:160]}..."

    inbox_item = InboxItem(
        user_id=recipient_id,
        type="POST_REPLY",
        payload_json={
            "reply_id": reply.id,
            "post_id": post.id,
            "post_type": post.type,
            "post_content": post_snippet,
            "reply_type": reply.type,
            "reply_message": reply.message,
            "sender": build_reply_user_out(current_user, sender_profile),
            "created_at": reply.created_at.isoformat(),
        },
    )
    db.add(inbox_item)
    db.commit()

    return PostReplyOut(
        id=reply.id,
        post_id=reply.post_id,
        owner_id=reply.owner_id,
        sender_id=reply.sender_id,
        recipient_id=reply.recipient_id,
        type=reply.type,
        message=reply.message,
        created_at=reply.created_at,
        sender=build_reply_user_out(current_user, sender_profile),
        caret_given=False,
        owner_reaction=None,
    )


@router.get("/{post_id}/replies", response_model=list[PostReplyOut])
def list_post_replies(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    ensure_post_owner(post.user_id, current_user.id, "Not allowed to view replies")

    rows = (
        db.query(PostReply, User, UserProfile, PostReplyCaret, PostReplyOwnerReaction)
        .join(User, User.id == PostReply.sender_id)
        .outerjoin(UserProfile, UserProfile.user_id == User.id)
        .outerjoin(PostReplyCaret, PostReplyCaret.reply_id == PostReply.id)
        .outerjoin(PostReplyOwnerReaction, PostReplyOwnerReaction.reply_id == PostReply.id)
        .filter(PostReply.post_id == post_id)
        .order_by(PostReply.created_at.desc())
        .all()
    )

    replies: list[PostReplyOut] = []
    for reply, sender, sender_profile, caret, reaction in rows:
        replies.append(
            PostReplyOut(
                id=reply.id,
                post_id=reply.post_id,
                owner_id=reply.owner_id,
                sender_id=reply.sender_id,
                recipient_id=reply.recipient_id,
                type=reply.type,
                message=reply.message,
                created_at=reply.created_at,
                sender=build_reply_user_out(sender, sender_profile),
                caret_given=bool(caret.is_given) if caret else False,
                owner_reaction=reaction.reaction if reaction else None,
            )
        )
    return replies




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

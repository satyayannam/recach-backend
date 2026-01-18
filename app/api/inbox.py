from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps_auth import get_current_user
from app.api.inbox_schemas import InboxItemOut
from app.api.post_reply_schemas import InboxPostCardOut, InboxPostReplyOut
from app.db.deps import get_db
from app.db.inbox_item import InboxItem
from app.db.models import User
from app.db.post import Post
from app.db.post_reply import PostReply
from app.db.post_reply_caret import PostReplyCaret
from app.db.post_reply_owner_reaction import PostReplyOwnerReaction
from app.db.user_profile import UserProfile

router = APIRouter(prefix="/api/inbox", tags=["Inbox"])
posts_router = APIRouter(prefix="/inbox", tags=["Inbox"])


@router.get("", response_model=list[InboxItemOut])
def list_inbox(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = (
        db.query(InboxItem)
        .filter(InboxItem.user_id == current_user.id)
        .order_by(InboxItem.created_at.desc())
        .all()
    )
    return items


@posts_router.get("/posts", response_model=list[InboxPostCardOut])
def list_inbox_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    posts = (
        db.query(Post)
        .filter(Post.user_id == current_user.id)
        .order_by(Post.created_at.desc())
        .all()
    )
    post_ids = [post.id for post in posts]
    replies_map: dict[int, list[InboxPostReplyOut]] = {post.id: [] for post in posts}

    if post_ids:
        rows = (
            db.query(PostReply, User, UserProfile, PostReplyCaret, PostReplyOwnerReaction)
            .join(User, User.id == PostReply.sender_id)
            .outerjoin(UserProfile, UserProfile.user_id == User.id)
            .outerjoin(PostReplyCaret, PostReplyCaret.reply_id == PostReply.id)
            .outerjoin(PostReplyOwnerReaction, PostReplyOwnerReaction.reply_id == PostReply.id)
            .filter(PostReply.post_id.in_(post_ids))
            .order_by(PostReply.created_at.desc())
            .all()
        )
        for reply, sender, sender_profile, caret, reaction in rows:
            replies_map.setdefault(reply.post_id, []).append(
                InboxPostReplyOut(
                    id=reply.id,
                    reply_type=reply.type,
                    message=reply.message,
                    created_at=reply.created_at,
                    sender={
                        "id": sender.id,
                        "username": sender.username,
                        "full_name": sender.full_name,
                        "profile_photo_url": sender_profile.profile_photo_url
                        if sender_profile
                        else None,
                    },
                    caret_given=bool(caret.is_given) if caret else False,
                    owner_reaction=reaction.reaction if reaction else None,
                )
            )

    output: list[InboxPostCardOut] = []
    for post in posts:
        snippet = post.content.strip()
        if len(snippet) > 160:
            snippet = f"{snippet[:160]}..."
        output.append(
            InboxPostCardOut(
                post_id=post.id,
                post_type=post.type,
                post_content=snippet,
                post_created_at=post.created_at,
                replies=replies_map.get(post.id, []),
            )
        )
    return output

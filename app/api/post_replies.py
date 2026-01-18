from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps_auth import get_current_user
from app.api.post_reply_schemas import (
    PostReplyCaretOut,
    PostReplyOwnerReactionIn,
    PostReplyOwnerReactionOut,
)
from app.db.deps import get_db
from app.db.inbox_item import InboxItem
from app.db.models import User
from app.db.post import Post
from app.db.post_reply import PostReply
from app.db.post_reply_caret import PostReplyCaret
from app.db.post_reply_owner_reaction import PostReplyOwnerReaction
from app.db.user_profile import UserProfile
from app.services.permissions import ensure_reply_owner

router = APIRouter(prefix="/post-replies", tags=["Post Replies"])

ALLOWED_REACTIONS = {"thanks", "helpful", "noted", "appreciate"}


def build_reply_user_out(user: User, profile: UserProfile | None):
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "profile_photo_url": profile.profile_photo_url if profile else None,
    }


@router.post("/{reply_id}/caret", response_model=PostReplyCaretOut)
def toggle_post_reply_caret(
    reply_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reply = db.query(PostReply).filter(PostReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    ensure_reply_owner(reply.owner_id, current_user.id, "Not allowed to toggle caret")

    caret = (
        db.query(PostReplyCaret)
        .filter(PostReplyCaret.reply_id == reply.id)
        .first()
    )
    if caret:
        caret.is_given = not caret.is_given
    else:
        caret = PostReplyCaret(
            reply_id=reply.id,
            post_owner_id=current_user.id,
            is_given=True,
        )
        db.add(caret)

    db.commit()
    return PostReplyCaretOut(reply_id=reply.id, is_given=caret.is_given)


@router.post("/{reply_id}/owner-reaction", response_model=PostReplyOwnerReactionOut)
def set_post_reply_owner_reaction(
    reply_id: int,
    payload: PostReplyOwnerReactionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reply = db.query(PostReply).filter(PostReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    ensure_reply_owner(reply.owner_id, current_user.id, "Not allowed to react")

    if payload.reaction not in ALLOWED_REACTIONS:
        raise HTTPException(status_code=400, detail="Invalid reaction")

    reaction = (
        db.query(PostReplyOwnerReaction)
        .filter(PostReplyOwnerReaction.reply_id == reply.id)
        .first()
    )
    created_notification = False
    if reaction:
        if reaction.reaction != payload.reaction:
            reaction.reaction = payload.reaction
            created_notification = True
    else:
        reaction = PostReplyOwnerReaction(
            reply_id=reply.id,
            post_owner_id=current_user.id,
            reaction=payload.reaction,
        )
        db.add(reaction)
        created_notification = True

    db.commit()
    db.refresh(reaction)

    if created_notification:
        post = db.query(Post).filter(Post.id == reply.post_id).first()
        post_snippet = post.content.strip() if post else ""
        if len(post_snippet) > 160:
            post_snippet = f"{post_snippet[:160]}..."

        sender_profile = (
            db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        )
        inbox_item = InboxItem(
            user_id=reply.sender_id,
            type="POST_REPLY_REACTION",
            payload_json={
                "reply_id": reply.id,
                "post_id": reply.post_id,
                "post_type": post.type if post else "",
                "post_content": post_snippet,
                "reaction": reaction.reaction,
                "sender": build_reply_user_out(current_user, sender_profile),
                "created_at": reaction.created_at.isoformat(),
            },
        )
        db.add(inbox_item)
        db.commit()

    return PostReplyOwnerReactionOut(
        id=reaction.id,
        reply_id=reaction.reply_id,
        post_owner_id=reaction.post_owner_id,
        reaction=reaction.reaction,
        created_at=reaction.created_at,
    )

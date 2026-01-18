from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PostReplyOwnerReactionType(str, PyEnum):
    thanks = "thanks"
    helpful = "helpful"
    noted = "noted"
    appreciate = "appreciate"


class PostReplyOwnerReaction(Base):
    __tablename__ = "post_reply_owner_reaction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reply_id: Mapped[int] = mapped_column(
        ForeignKey("post_replies.id"), unique=True, nullable=False
    )
    post_owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    reaction: Mapped[str] = mapped_column(
        SAEnum(PostReplyOwnerReactionType, name="post_reply_reaction"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PostReplyCaret(Base):
    __tablename__ = "post_reply_carets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reply_id: Mapped[int] = mapped_column(
        ForeignKey("post_replies.id"), unique=True, nullable=False
    )
    post_owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_given: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

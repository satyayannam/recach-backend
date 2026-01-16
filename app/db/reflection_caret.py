from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReflectionCaret(Base):
    __tablename__ = "reflection_carets"
    __table_args__ = (UniqueConstraint("reflection_id", "user_id", name="uq_reflection_caret"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reflection_id: Mapped[int] = mapped_column(ForeignKey("reflections.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

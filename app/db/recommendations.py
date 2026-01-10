from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    recommender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    rec_type: Mapped[str] = mapped_column(String(50), nullable=False)   # job / academic / project / leadership
    reason: Mapped[str] = mapped_column(String(500), nullable=False)

    # Filled only when APPROVED
    note_title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    note_body: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


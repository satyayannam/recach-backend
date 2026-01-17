import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserCourse(Base):
    __tablename__ = "user_courses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    course_name: Mapped[str] = mapped_column(Text, nullable=False)
    course_number: Mapped[str] = mapped_column(String(50), nullable=False)
    professor: Mapped[str | None] = mapped_column(Text, nullable=True)
    grade: Mapped[str] = mapped_column(String(20), nullable=False)
    program_level: Mapped[str] = mapped_column(String(20), nullable=False)
    term: Mapped[str | None] = mapped_column(String(40), nullable=True)
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="PUBLIC")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

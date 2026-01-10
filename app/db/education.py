from sqlalchemy import String, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from sqlalchemy import Column, String, DateTime


class EducationEntry(Base):
    __tablename__ = "education_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    degree_type: Mapped[str] = mapped_column(String(20), nullable=False)  # bachelor/master/phd
    university_name: Mapped[str] = mapped_column(String(255), nullable=False)
    university_tier: Mapped[int] = mapped_column(Integer, nullable=False)  # 1–5

    gpa: Mapped[float | None] = mapped_column(Float, nullable=True)

    start_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[Date | None] = mapped_column(Date, nullable=True)

    is_completed: Mapped[bool] = mapped_column(default=True, nullable=False)
    college_id: Mapped[str] = mapped_column(String(50), nullable=False)
    verification_status = Column(String, nullable=False, default="PENDING")
    verified_at = Column(DateTime, nullable=True)


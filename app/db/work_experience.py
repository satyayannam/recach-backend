from sqlalchemy import String, Integer, Date, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from sqlalchemy import Column, String, DateTime
from datetime import datetime

class WorkExperience(Base):
    __tablename__ = "work_experiences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    employment_type: Mapped[str] = mapped_column(String(50), nullable=False)  # internship / full_time / part_time / contract
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    verification_status = Column(String, nullable=False, default="PENDING")
    verified_at = Column(DateTime, nullable=True)


from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base  # wherever your Base is

class VerificationRequest(Base):
    __tablename__ = "verification_requests"

    id = Column(Integer, primary_key=True, index=True)

    owner_user_id = Column(Integer, nullable=False, index=True)

    subject_type = Column(String, nullable=False)  # "EDUCATION" or "WORK"
    subject_id = Column(Integer, nullable=False, index=True)

    status = Column(String, nullable=False, default="PENDING")  # PENDING/VERIFIED/REJECTED

    contact_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    contact_phone = Column(String, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    decided_at = Column(DateTime, nullable=True)
    decided_by_user_id = Column(Integer, nullable=True)
    admin_notes = Column(String, nullable=True)

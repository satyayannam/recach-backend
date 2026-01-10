from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class CredentialDocument(Base):
    __tablename__ = "credential_documents"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    doc_type = Column(String(50), nullable=False)  # transcript / exam / employment / other
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    file_path = Column(Text, nullable=False)       # store path for MVP (later S3)
    file_name = Column(String(255), nullable=False)

    verifier_name = Column(String(200), nullable=True)
    verifier_email = Column(String(200), nullable=True)
    verifier_phone = Column(String(50), nullable=True)
    verifier_role = Column(String(100), nullable=True)  # advisor/supervisor/etc

    status = Column(String(30), default="PENDING", nullable=False)  # PENDING/APPROVED/REJECTED
    admin_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)


class CredentialAccessRequest(Base):
    __tablename__ = "credential_access_requests"

    id = Column(Integer, primary_key=True, index=True)
    credential_id = Column(Integer, ForeignKey("credential_documents.id"), index=True, nullable=False)
    requester_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    message = Column(Text, nullable=True)

    status = Column(String(30), default="PENDING", nullable=False)  # PENDING/APPROVED/REJECTED
    decided_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

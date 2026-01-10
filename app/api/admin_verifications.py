# app/api/admin_verifications.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.verification_request import VerificationRequest
from app.db.education import EducationEntry
from app.db.work_experience import WorkExperience

from app.api.admin_auth import get_current_admin
from app.api.admin_deps import admin_required



router = APIRouter(prefix="/admin/verifications", tags=["Admin Verifications"])

PENDING = "PENDING"
APPROVED = "APPROVED"
REJECTED = "REJECTED"
VERIFIED = "VERIFIED"


class VerificationRequestOut(BaseModel):
    id: int
    owner_user_id: int
    subject_type: str
    subject_id: int
    status: str
    contact_name: str
    contact_email: str
    contact_phone: Optional[str] = None
    created_at: datetime
    decided_at: Optional[datetime] = None
    decided_by_user_id: Optional[int] = None
    admin_notes: Optional[str] = None

    class Config:
        from_attributes = True


class DecisionIn(BaseModel):
    admin_notes: Optional[str] = None


def _get_subject_row(db: Session, subject_type: str, subject_id: int):
    st = subject_type.strip().lower()

    if st in ("education", "edu"):
        row = db.query(EducationEntry).filter(EducationEntry.id == subject_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Education entry not found")
        return "education", row

    if st in ("work", "work_experience", "experience"):
        row = db.query(WorkExperience).filter(WorkExperience.id == subject_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Work entry not found")
        return "work", row

    raise HTTPException(status_code=400, detail=f"Invalid subject_type: {subject_type}")


@router.get("", response_model=List[VerificationRequestOut], operation_id="admin_list_verifications")
def list_verifications(
    status: str = Query(PENDING),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),

):
    items = (
        db.query(VerificationRequest)
        .filter(VerificationRequest.status == status.upper())
        .order_by(VerificationRequest.created_at.desc())
        .all()
    )
    return items


@router.post("/{request_id}/approve", response_model=VerificationRequestOut, operation_id="admin_approve_verification")
def approve_verification(
    request_id: int,
    payload: DecisionIn,
    db: Session = Depends(get_db),
    admin_payload=Depends(admin_required),
):
    req = db.query(VerificationRequest).filter(VerificationRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Verification request not found")

    if req.status != PENDING:
        raise HTTPException(status_code=400, detail=f"Request already {req.status}")

    _type, row = _get_subject_row(db, req.subject_type, req.subject_id)
    now = datetime.utcnow()

    row.verification_status = VERIFIED
    row.verified_at = now

    req.status = APPROVED
    req.decided_at = now

    # Since admin isn't a DB user row, keep decided_by_user_id null and store email in notes.
    req.decided_by_user_id = None
    req.admin_notes = (payload.admin_notes or "").strip() or None
    admin_sub = (admin_payload or {}).get("sub", "")
    if isinstance(admin_sub, str) and admin_sub.startswith("admin:"):
        admin_email = admin_sub.split("admin:", 1)[1].strip()
        if admin_email:
            req.admin_notes = f"[admin:{admin_email}] " + (req.admin_notes or "")

    db.commit()
    db.refresh(req)
    return req


@router.post("/{request_id}/reject", response_model=VerificationRequestOut, operation_id="admin_reject_verification")
def reject_verification(
    request_id: int,
    payload: DecisionIn,
    db: Session = Depends(get_db),
    admin_payload=Depends(admin_required),
):
    req = db.query(VerificationRequest).filter(VerificationRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Verification request not found")

    if req.status != PENDING:
        raise HTTPException(status_code=400, detail=f"Request already {req.status}")

    _type, row = _get_subject_row(db, req.subject_type, req.subject_id)
    now = datetime.utcnow()

    row.verification_status = REJECTED
    row.verified_at = None

    req.status = REJECTED
    req.decided_at = now
    req.decided_by_user_id = None

    req.admin_notes = (payload.admin_notes or "").strip() or None
    admin_sub = (admin_payload or {}).get("sub", "")
    if isinstance(admin_sub, str) and admin_sub.startswith("admin:"):
        admin_email = admin_sub.split("admin:", 1)[1].strip()
        if admin_email:
            req.admin_notes = f"[admin:{admin_email}] " + (req.admin_notes or "")

    db.commit()
    db.refresh(req)
    return req

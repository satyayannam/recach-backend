# app/api/work.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.work_experience import WorkExperience
from app.db.verification_request import VerificationRequest
from app.api.work_schemas import WorkCreate, WorkOut
from app.api.deps_auth import get_current_user

router = APIRouter(prefix="/work", tags=["work"])


@router.post("", response_model=WorkOut)
def add_work(
    payload: WorkCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if payload.is_current and payload.end_date is not None:
        raise HTTPException(status_code=400, detail="If is_current is true, end_date must be null")

    # 1) create work entry
    entry = WorkExperience(
        user_id=current_user.id,
        company_name=payload.company_name,
        title=payload.title,
        employment_type=payload.employment_type,
        is_current=payload.is_current,
        start_date=payload.start_date,
        end_date=payload.end_date,
        verification_status="PENDING",
        verified_at=None,
    )
    db.add(entry)
    db.flush()  # entry.id now exists

    # 2) pull verification contact info from whatever schema is available
    supervisor_name = getattr(payload, "supervisor_name", None)
    supervisor_email = getattr(payload, "supervisor_email", None)
    supervisor_phone = getattr(payload, "supervisor_phone", None)

    contact_name = getattr(payload, "contact_name", None)
    contact_email = getattr(payload, "contact_email", None)
    contact_phone = getattr(payload, "contact_phone", None)

    # choose primary contact
    primary_name = supervisor_name or contact_name
    primary_email = supervisor_email or contact_email
    primary_phone = supervisor_phone or contact_phone

    if not primary_name or not primary_email:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail="Verification contact missing. Provide supervisor_name+supervisor_email (preferred) or contact_name+contact_email.",
        )

    # admin notes: if both exist, store the "other" one as extra info
    admin_notes = None
    if supervisor_name and contact_name:
        admin_notes=(
    f"Additional contact: {payload.contact_name} / {payload.contact_email}"
    + (f" / {payload.contact_phone}" if payload.contact_phone else "")
    if payload.contact_name and payload.contact_email
    else None
),


    # 3) create verification request
    vr = VerificationRequest(
        owner_user_id=current_user.id,
        subject_type="work",
        subject_id=entry.id,
        status="PENDING",
        contact_name=primary_name,
        contact_email=str(primary_email),
        contact_phone=primary_phone,
        admin_notes=admin_notes,
    )

    db.add(vr)
    db.commit()
    db.refresh(entry)
    return entry

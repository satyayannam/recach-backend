from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.education import EducationEntry
from app.db.verification_request import VerificationRequest
from app.api.education_schemas import EducationCreate, EducationOut
from app.api.deps_auth import get_current_user
from app.data.colleges import get_college_by_id, DEFAULT_TIER_FOR_OTHER_COLLEGES


router = APIRouter(prefix="/education", tags=["education"])


@router.post("", response_model=EducationOut)
def add_education(
    payload: EducationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # ---- Resolve college metadata ----
    college = get_college_by_id(payload.college_id)

    if college:
        university_name = college["name"]
        university_tier = college["tier"]
    else:
        university_name = "Other / Not Listed"
        university_tier = DEFAULT_TIER_FOR_OTHER_COLLEGES

    # ---- Create education entry (DB-only fields) ----
    entry = EducationEntry(
        user_id=current_user.id,
        degree_type=payload.degree_type,
        college_id=payload.college_id.strip().lower(),
        university_name=university_name,
        university_tier=university_tier,
        gpa=payload.gpa,
        start_date=payload.start_date,
        end_date=payload.end_date,
        is_completed=payload.is_completed,
        verification_status="PENDING",
        verified_at=None,
    )

    db.add(entry)
    db.flush()  # so entry.id exists

    # ---- Optional extra contact fields (only if your schema has them) ----
    extra_contact_name = getattr(payload, "contact_name", None)
    extra_contact_email = getattr(payload, "contact_email", None)
    extra_contact_phone = getattr(payload, "contact_phone", None)

    admin_notes = None
    if extra_contact_name or extra_contact_email or extra_contact_phone:
        admin_notes = (
            f"Additional contact provided: {extra_contact_name or '-'} / "
            f"{str(extra_contact_email) if extra_contact_email else '-'}"
            + (f" / {extra_contact_phone}" if extra_contact_phone else "")
        )

    # ---- Create verification request ----
    verification = VerificationRequest(
        owner_user_id=current_user.id,
        subject_type="education",
        subject_id=entry.id,
        status="PENDING",
        contact_name=payload.advisor_name,
        contact_email=str(payload.advisor_email),
        contact_phone=getattr(payload, "advisor_phone", None),
        admin_notes=admin_notes,
    )

    db.add(verification)
    db.commit()
    db.refresh(entry)

    return entry

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.contact_schemas import ContactMethodIn, ContactMethodOut, CONTACT_METHODS
from app.api.deps_auth import get_current_user
from app.db.contact_method import ContactMethod
from app.db.deps import get_db
from app.db.models import User

router = APIRouter(prefix="/api/profile/contact-method", tags=["Contact Methods"])


@router.put("", response_model=ContactMethodOut, status_code=status.HTTP_200_OK)
def set_contact_method(
    payload: ContactMethodIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.method not in CONTACT_METHODS:
        raise HTTPException(status_code=400, detail="Invalid contact method")

    existing = (
        db.query(ContactMethod).filter(ContactMethod.user_id == current_user.id).first()
    )
    if existing:
        existing.method = payload.method
        existing.value = payload.value.strip()
        db.commit()
        db.refresh(existing)
        return existing

    entry = ContactMethod(
        user_id=current_user.id,
        method=payload.method,
        value=payload.value.strip(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/me", response_model=ContactMethodOut)
def get_my_contact_method(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = (
        db.query(ContactMethod).filter(ContactMethod.user_id == current_user.id).first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Contact method not set")
    return entry

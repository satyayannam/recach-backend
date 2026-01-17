from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.contact_schemas import ContactRequestIn, ContactRequestOut, ContactRevealOut
from app.api.deps_auth import get_current_user
from app.db.contact_request import ContactRequest
from app.db.contact_method import ContactMethod
from app.db.deps import get_db
from app.db.inbox_item import InboxItem
from app.db.models import User
from app.db.user_course import UserCourse
from app.db.user_profile import UserProfile

router = APIRouter(prefix="/api/contact-requests", tags=["Contact Requests"])


def _rate_limit(db: Session, requester_id: int, max_per_day: int = 10):
    since = datetime.utcnow() - timedelta(days=1)
    count = (
        db.query(ContactRequest)
        .filter(
            ContactRequest.requester_id == requester_id,
            ContactRequest.created_at >= since,
        )
        .count()
    )
    if count >= max_per_day:
        raise HTTPException(status_code=429, detail="Daily contact request limit reached")


@router.post("", response_model=ContactRequestOut, status_code=status.HTTP_201_CREATED)
def create_contact_request(
    payload: ContactRequestIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.target_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot request yourself")

    course = db.query(UserCourse).filter(UserCourse.id == payload.course_id).first()
    if not course or course.user_id != payload.target_id:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.visibility != "PUBLIC" and course.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Course is not public")

    _rate_limit(db, current_user.id)

    existing = (
        db.query(ContactRequest)
        .filter(
            ContactRequest.requester_id == current_user.id,
            ContactRequest.target_id == payload.target_id,
            ContactRequest.course_id == payload.course_id,
            ContactRequest.status.in_(["PENDING", "ACCEPTED"]),
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Contact request already exists")

    request = ContactRequest(
        requester_id=current_user.id,
        target_id=payload.target_id,
        course_id=payload.course_id,
        message=payload.message.strip() if payload.message else None,
        status="PENDING",
    )
    db.add(request)
    db.flush()

    target_profile = (
        db.query(UserProfile).filter(UserProfile.user_id == payload.target_id).first()
    )
    course_university = None
    if target_profile and isinstance(target_profile.university_names, list) and target_profile.university_names:
        course_university = str(target_profile.university_names[0])

    inbox_item = InboxItem(
        user_id=payload.target_id,
        type="CONTACT_REQUEST",
        status="PENDING",
        payload_json={
            "request_id": str(request.id),
            "requester_id": current_user.id,
            "requester_name": current_user.full_name,
            "requester_username": current_user.username,
            "course_id": str(course.id),
            "course_number": course.course_number,
            "course_name": course.course_name,
            "university": course_university,
        },
    )
    db.add(inbox_item)
    db.commit()
    db.refresh(request)
    return request


@router.post("/{request_id}/accept", status_code=status.HTTP_200_OK)
def accept_contact_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    request = db.query(ContactRequest).filter(ContactRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    if request.target_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to accept this request")
    if request.status != "PENDING":
        raise HTTPException(status_code=409, detail="Request already handled")

    request.status = "ACCEPTED"
    request.responded_at = datetime.utcnow()

    inbox_item = (
        db.query(InboxItem)
        .filter(
            InboxItem.user_id == current_user.id,
            InboxItem.type == "CONTACT_REQUEST",
            InboxItem.payload_json["request_id"].astext == str(request_id),
        )
        .first()
    )
    if inbox_item:
        inbox_item.status = "ACCEPTED"

    contact = (
        db.query(ContactMethod).filter(ContactMethod.user_id == current_user.id).first()
    )
    accepted_notice = InboxItem(
        user_id=request.requester_id,
        type="CONTACT_ACCEPTED",
        status="UNREAD",
        payload_json={
            "request_id": str(request.id),
            "target_id": current_user.id,
            "target_name": current_user.full_name,
            "target_username": current_user.username,
            "course_id": str(request.course_id),
            "contact_method": contact.method if contact else None,
        },
    )
    db.add(accepted_notice)

    db.commit()
    return {"status": "accepted"}


@router.post("/{request_id}/ignore", status_code=status.HTTP_200_OK)
def ignore_contact_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    request = db.query(ContactRequest).filter(ContactRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    if request.target_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to ignore this request")
    if request.status != "PENDING":
        raise HTTPException(status_code=409, detail="Request already handled")

    request.status = "IGNORED"
    request.responded_at = datetime.utcnow()

    inbox_item = (
        db.query(InboxItem)
        .filter(
            InboxItem.user_id == current_user.id,
            InboxItem.type == "CONTACT_REQUEST",
            InboxItem.payload_json["request_id"].astext == str(request_id),
        )
        .first()
    )
    if inbox_item:
        inbox_item.status = "IGNORED"

    db.commit()
    return {"status": "ignored"}


@router.get("/{request_id}/contact", response_model=ContactRevealOut)
def get_contact_for_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    request = db.query(ContactRequest).filter(ContactRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    if request.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to view contact")
    if request.status != "ACCEPTED":
        raise HTTPException(status_code=403, detail="Contact not available")

    contact = (
        db.query(ContactMethod).filter(ContactMethod.user_id == request.target_id).first()
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact method not set")
    return ContactRevealOut(method=contact.method, value=contact.value)

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps_auth import get_current_user
from app.db.deps import get_db
from app.db.models import User
from app.db.recommendations import Recommendation
from app.db.inbox_item import InboxItem
from app.services.username import normalize_username
from app.api.recommendation_schemas import (
    RecommendationRequestIn,
    RecommendationApproveIn,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


# -------------------------
# Request recommendation
# requester = logged-in user
# -------------------------
@router.post("/request", status_code=status.HTTP_201_CREATED)
def request_recommendation(
    payload: RecommendationRequestIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    requester_id = current_user.id

    # recommender lookup by username (supports "^name" or "name")
    try:
        rec_uname = normalize_username(payload.recommender_username)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid recommender username")

    recommender = db.query(User).filter(User.username == rec_uname).first()
    if not recommender:
        raise HTTPException(status_code=404, detail="Recommender not found")

    if recommender.id == requester_id:
        raise HTTPException(status_code=400, detail="You cannot request recommendation from yourself")

    # prevent duplicates while pending
    existing = (
        db.query(Recommendation)
        .filter(
            Recommendation.requester_id == requester_id,
            Recommendation.recommender_id == recommender.id,
            Recommendation.status == "PENDING",
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="A pending recommendation request already exists")

    rec = Recommendation(
        requester_id=requester_id,
        recommender_id=recommender.id,
        rec_type=payload.rec_type,
        reason=payload.reason,
        status="PENDING",
    )

    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


# -------------------------
# Pending requests for me (as recommender)
# shows what I need to approve/reject
# -------------------------
@router.get("/pending", status_code=status.HTTP_200_OK)
def get_my_pending_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recs = (
        db.query(Recommendation)
        .filter(
            Recommendation.recommender_id == current_user.id,
            Recommendation.status == "PENDING",
        )
        .order_by(Recommendation.created_at.desc())
        .all()
    )

    # return enriched payload (includes requester username/name)
    out = []
    for r in recs:
        requester = db.query(User).filter(User.id == r.requester_id).first()
        out.append(
            {
                "id": r.id,
                "rec_type": r.rec_type,
                "reason": r.reason,
                "status": r.status,
                "created_at": r.created_at,
                "requester": {
                    "id": requester.id,
                    "full_name": requester.full_name,
                    "username": requester.username,
                }
                if requester
                else None,
            }
        )
    return out


# -------------------------
# Approve (only recommender)
# -------------------------
@router.post("/{recommendation_id}/approve", status_code=status.HTTP_200_OK)
def approve_recommendation(
    recommendation_id: int,
    payload: RecommendationApproveIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if rec.recommender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the recommender can approve this")

    if rec.status != "PENDING":
        raise HTTPException(status_code=409, detail=f"Cannot approve a {rec.status} recommendation")

    rec.status = "APPROVED"
    rec.note_title = payload.note_title
    rec.note_body = payload.note_body
    rec.decided_at = datetime.utcnow()

    inbox_item = InboxItem(
        user_id=rec.requester_id,
        type="RECOMMENDATION_APPROVED",
        status="UNREAD",
        payload_json={
            "recommendation_id": rec.id,
            "recommender_id": current_user.id,
            "recommender_name": current_user.full_name,
            "recommender_username": current_user.username,
            "note_title": rec.note_title,
            "note_body": rec.note_body,
        },
    )
    db.add(inbox_item)

    db.commit()
    db.refresh(rec)
    return rec


# -------------------------
# Reject (only recommender)
# -------------------------
@router.post("/{recommendation_id}/reject", status_code=status.HTTP_200_OK)
def reject_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if rec.recommender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the recommender can reject this")

    if rec.status != "PENDING":
        raise HTTPException(status_code=409, detail=f"Cannot reject a {rec.status} recommendation")

    rec.status = "REJECTED"
    rec.decided_at = datetime.utcnow()

    db.commit()
    db.refresh(rec)
    return rec

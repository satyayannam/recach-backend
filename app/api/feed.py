from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.deps import get_db
from app.db.verification_request import VerificationRequest
from app.db.recommendations import Recommendation
from app.db.models import User  # <-- change this import to the actual file where User is defined

router = APIRouter(prefix="/feed", tags=["Feed"])


@router.get("")
def get_feed(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    # Verifications (approved)
    verifications = (
        db.query(VerificationRequest)
        .filter(VerificationRequest.status == "APPROVED")
        .order_by(desc(VerificationRequest.decided_at), desc(VerificationRequest.created_at))
        .limit(limit)
        .all()
    )

    # Recommendations (approved)
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.status == "APPROVED")
        .order_by(desc(getattr(Recommendation, "created_at", Recommendation.recommender_id)))
        .limit(limit)
        .all()
    )

    items = []

    # Verification events
    for vr in verifications:
        user = db.query(User).filter(User.id == vr.owner_user_id).first()
        ts = vr.decided_at or vr.created_at

        items.append(
            {
                "type": "verification",
                "timestamp": ts,
                "user": {
                    "id": vr.owner_user_id,
                    "full_name": user.full_name if user else None,
                },
                "payload": {
                    "verification_request_id": vr.id,
                    "subject_type": vr.subject_type,   # "education" | "work"
                    "subject_id": vr.subject_id,
                    "status": vr.status,               # "APPROVED"
                },
                "message": f"{(user.full_name if user else 'A user')}'s {vr.subject_type} was VERIFIED",
            }
        )

    # Recommendation events
    for r in recs:
        receiver = db.query(User).filter(User.id == r.requester_id).first()
        recommender = db.query(User).filter(User.id == r.recommender_id).first()

        ts = getattr(r, "created_at", None)  # if your model doesn't have it, this becomes None

        items.append(
            {
                "type": "recommendation",
                "timestamp": ts,
                "user": {
                    "id": r.requester_id,
                    "full_name": receiver.full_name if receiver else None,
                },
                "payload": {
                    "receiver_id": r.requester_id,
                    "recommender_id": r.recommender_id,
                    "rec_type": getattr(r, "rec_type", None),
                    "status": r.status,  # "APPROVED"
                },
                "message": f"{(recommender.full_name if recommender else 'Someone')} recommended {(receiver.full_name if receiver else 'a user')}",
            }
        )

    # sort newest first (None timestamps go last)
    def sort_key(x):
        ts = x["timestamp"]
        return (ts is not None, ts)

    items.sort(key=sort_key, reverse=True)
    return items[:limit]

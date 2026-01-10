from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.models import User  # <-- change to your actual User file
from app.services.scores import get_achievement_total, get_recommendation_total

router = APIRouter(prefix="/leaderboard", tags=["Leaderboards"])


@router.get("/achievements")
def achievement_leaderboard(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    users = db.query(User).all()

    rows = []
    for u in users:
        score = get_achievement_total(db, u.id)
        rows.append(
            {
                "user": {"id": u.id, "full_name": u.full_name},
                "score": score,
            }
        )

    rows.sort(key=lambda r: r["score"], reverse=True)

    for i, r in enumerate(rows[:limit], start=1):
        r["rank"] = i

    return rows[:limit]


@router.get("/recommendations")
def recommendation_leaderboard(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    users = db.query(User).all()

    rows = []
    for u in users:
        score = get_recommendation_total(db, u.id)
        rows.append(
            {
                "user": {"id": u.id, "full_name": u.full_name},
                "score": score,
            }
        )

    rows.sort(key=lambda r: r["score"], reverse=True)

    for i, r in enumerate(rows[:limit], start=1):
        r["rank"] = i

    return rows[:limit]

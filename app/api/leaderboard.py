from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.models import User
from app.services.scores import get_achievement_total, get_recommendation_total

router = APIRouter(prefix="/leaderboard", tags=["Leaderboards"])

def _percent_rank(values: list[int]) -> dict[int, float]:
    if not values:
        return {}

    n = len(values)
    if n == 1:
        return {values[0]: 1.0}

    sorted_vals = sorted(values, reverse=True)
    score_to_rank: dict[int, int] = {}
    for idx, score in enumerate(sorted_vals, start=1):
        if score not in score_to_rank:
            score_to_rank[score] = idx

    score_to_percent: dict[int, float] = {}
    for score, rank in score_to_rank.items():
        score_to_percent[score] = (n - rank) / (n - 1)

    return score_to_percent


@router.get("/combined")
def combined_leaderboard(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    users = db.query(User).all()

    rows = []
    achievement_scores: list[int] = []
    recommendation_scores: list[int] = []

    for u in users:
        achievement_score = get_achievement_total(db, u.id)
        recommendation_score = get_recommendation_total(db, u.id)
        achievement_scores.append(achievement_score)
        recommendation_scores.append(recommendation_score)
        rows.append(
            {
                "user": {"id": u.id, "full_name": u.full_name, "username": u.username},
                "achievement_score": achievement_score,
                "recommendation_score": recommendation_score,
            }
        )

    pA_map = _percent_rank(achievement_scores)
    pR_map = _percent_rank(recommendation_scores)

    for row in rows:
        pA = pA_map.get(row["achievement_score"], 0.0)
        pR = pR_map.get(row["recommendation_score"], 0.0)
        row["pA"] = pA
        row["pR"] = pR
        row["combined_score"] = (0.6 * pA) + (0.4 * pR)

    rows.sort(
        key=lambda r: (
            r["combined_score"],
            r["pA"],
            r["pR"],
            r["achievement_score"],
        ),
        reverse=True,
    )

    for i, r in enumerate(rows[:limit], start=1):
        r["rank"] = i

    return rows[:limit]


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
                "user": {"id": u.id, "full_name": u.full_name, "username": u.username},
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
                "user": {"id": u.id, "full_name": u.full_name, "username": u.username},
                "score": score,
            }
        )

    rows.sort(key=lambda r: r["score"], reverse=True)

    for i, r in enumerate(rows[:limit], start=1):
        r["rank"] = i

    return rows[:limit]

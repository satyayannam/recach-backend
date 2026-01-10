from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.models import User
from app.db.education import EducationEntry
from app.db.work_experience import WorkExperience

from app.scoring.education_score import score_education_entry
from app.scoring.work_score import score_work_entry
from app.scoring.work_streak import compute_company_streaks


def compute_user_achievement(db: Session, user_id: int) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    education_entries = (
        db.query(EducationEntry)
        .filter(EducationEntry.user_id == user_id)
        .order_by(EducationEntry.id.asc())
        .all()
    )

    education_total = 0
    education_breakdown = []

    for e in education_entries:
        scored = score_education_entry(
            university_tier=e.university_tier,
            degree_type=e.degree_type,
            is_completed=e.is_completed,
            gpa=e.gpa,
        )
        education_total += scored["total"]
        education_breakdown.append({
            "education_id": e.id,
            "degree_type": e.degree_type,
            "college_id": e.college_id,
            "university_name": e.university_name,
            "university_tier": e.university_tier,
            "gpa": e.gpa,
            "score": scored["total"],
            "breakdown": scored["breakdown"],
        })

    work_entries = (
        db.query(WorkExperience)
        .filter(WorkExperience.user_id == user_id)
        .order_by(WorkExperience.id.asc())
        .all()
    )

    streak_total, streak_breakdown = compute_company_streaks(work_entries)

    work_total = 0
    work_breakdown = []

    for w in work_entries:
        end_dt = w.end_date
        if w.is_current or end_dt is None:
            end_dt = date.today()

        scored = score_work_entry(
            employment_type=w.employment_type,
            start_date=w.start_date,
            end_date=end_dt,
        )

        work_total += scored["total"]
        work_breakdown.append({
            "work_id": w.id,
            "company_name": w.company_name,
            "title": w.title,
            "employment_type": w.employment_type,
            "start_date": w.start_date,
            "end_date": w.end_date,
            "is_current": w.is_current,
            "score": scored["total"],
            "breakdown": scored["breakdown"],
        })

    achievement_total = education_total + work_total + streak_total

    return {
        "achievement_score": {
            "total": achievement_total,
            "education_total": education_total,
            "work_total": work_total,
            "work_streak_total": streak_total,
            "education_count": len(education_entries),
            "work_count": len(work_entries),
            "education_breakdown": education_breakdown,
            "work_breakdown": work_breakdown,
            "work_streak_breakdown": streak_breakdown,
        }
    }

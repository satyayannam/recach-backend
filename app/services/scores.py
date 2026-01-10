from sqlalchemy.orm import Session
from datetime import date

from app.db.education import EducationEntry
from app.db.work_experience import WorkExperience
from app.db.recommendations import Recommendation

from app.scoring.education_score import score_education_entry
from app.scoring.work_score import score_work_entry
from app.scoring.work_streak import compute_company_streaks
from app.scoring.recommendation_score import points_for_recommendation


VERIFIED = "VERIFIED"


def get_achievement_total(db: Session, user_id: int) -> int:
    # ✅ Only VERIFIED education counts
    education_entries = (
        db.query(EducationEntry)
        .filter(EducationEntry.user_id == user_id)
        .filter(EducationEntry.verification_status == VERIFIED)
        .order_by(EducationEntry.id.asc())
        .all()
    )

    education_total = 0
    for e in education_entries:
        scored = score_education_entry(
            university_tier=e.university_tier,
            degree_type=e.degree_type,
            is_completed=e.is_completed,
            gpa=e.gpa,
        )
        education_total += scored["total"]

    # ✅ Only VERIFIED work counts
    work_entries = (
        db.query(WorkExperience)
        .filter(WorkExperience.user_id == user_id)
        .filter(WorkExperience.verification_status == VERIFIED)
        .order_by(WorkExperience.id.asc())
        .all()
    )

    # ✅ streak only from VERIFIED work entries
    streak_total, _streak_breakdown = compute_company_streaks(work_entries)

    work_total = 0
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

    return education_total + work_total + streak_total


def get_recommendation_total(db: Session, user_id: int) -> int:
    # all APPROVED recs received by this user
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.requester_id == user_id)
        .filter(Recommendation.status == "APPROVED")
        .order_by(Recommendation.id.asc())
        .all()
    )

    total = 0
    for r in recs:
        recommender_achievement_total = get_achievement_total(db, r.recommender_id)
        scored = points_for_recommendation(r.rec_type, recommender_achievement_total)
        total += scored["points"]

    return total

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.education import EducationEntry
from app.scoring.education_score import score_education_entry

router = APIRouter(prefix="/education", tags=["education"])


@router.get("/{education_id}/score")
def get_education_score(education_id: int, db: Session = Depends(get_db)):
    entry = db.query(EducationEntry).filter(EducationEntry.id == education_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Education entry not found")

    scored = score_education_entry(
        university_tier=entry.university_tier,
        degree_type=entry.degree_type,
        is_completed=entry.is_completed,
        gpa=entry.gpa,
    )

    return {
        "education_id": entry.id,
        "user_id": entry.user_id,
        "degree_type": entry.degree_type,
        "college_id": entry.college_id,
        "university_name": entry.university_name,
        "university_tier": entry.university_tier,
        "gpa": entry.gpa,
        **scored,
    }

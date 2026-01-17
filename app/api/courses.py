from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.course_schemas import (
    CourseCreate,
    CourseOut,
    CoursePersonOut,
    CourseSearchGroup,
    PROGRAM_LEVELS,
    VISIBILITY_LEVELS,
)
from app.api.deps_auth import get_current_user, get_optional_user
from app.db.deps import get_db
from app.db.models import User
from app.db.user_course import UserCourse
from app.db.contact_request import ContactRequest
from app.db.user_profile import UserProfile
from app.db.education import EducationEntry

router = APIRouter(prefix="/api/courses", tags=["Courses"])


def _validate_course_input(payload: CourseCreate):
    if payload.program_level not in PROGRAM_LEVELS:
        raise HTTPException(status_code=400, detail="Invalid program level")
    if payload.visibility not in VISIBILITY_LEVELS:
        raise HTTPException(status_code=400, detail="Invalid visibility")


@router.post("", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_course_input(payload)
    has_verified_edu = (
        db.query(EducationEntry)
        .filter(
            EducationEntry.user_id == current_user.id,
            EducationEntry.verification_status == "VERIFIED",
        )
        .first()
        is not None
    )
    if not has_verified_edu:
        raise HTTPException(status_code=403, detail="Verified education required")
    course = UserCourse(
        user_id=current_user.id,
        course_name=payload.course_name.strip(),
        course_number=payload.course_number.strip(),
        professor=payload.professor.strip() if payload.professor else None,
        grade=payload.grade.strip(),
        program_level=payload.program_level,
        term=payload.term.strip() if payload.term else None,
        visibility=payload.visibility,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/me", response_model=list[CourseOut])
def list_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(UserCourse)
        .filter(UserCourse.user_id == current_user.id)
        .order_by(UserCourse.created_at.desc())
        .all()
    )


@router.delete("/{course_id}")
def delete_course(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.query(UserCourse).filter(UserCourse.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this course")
    db.delete(course)
    db.commit()
    return {"status": "deleted"}


@router.get("/search", response_model=list[CourseSearchGroup])
def search_courses(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    query = (
        db.query(UserCourse, User)
        .join(User, User.id == UserCourse.user_id)
        .filter(
            or_(
                UserCourse.course_name.ilike(f"%{q}%"),
                UserCourse.course_number.ilike(f"%{q}%"),
            )
        )
    )

    courses = query.all()
    user_ids = {course.user_id for (course, _) in courses}
    profiles = (
        db.query(UserProfile).filter(UserProfile.user_id.in_(user_ids)).all()
        if user_ids
        else []
    )
    profile_map = {profile.user_id: profile for profile in profiles}
    edu_rows = (
        db.query(EducationEntry.user_id, EducationEntry.university_name)
        .filter(
            EducationEntry.user_id.in_(user_ids),
            EducationEntry.verification_status == "VERIFIED",
        )
        .all()
        if user_ids
        else []
    )
    edu_map: dict[int, str] = {}
    for user_id, university_name in edu_rows:
        if user_id not in edu_map:
            edu_map[user_id] = university_name

    visible = []
    for course, user in courses:
        if course.visibility == "PUBLIC":
            visible.append((course, user))
        elif current_user and course.user_id == current_user.id:
            visible.append((course, user))
        else:
            # Treat CIRCLE as PRIVATE until circle feature exists.
            continue

    request_map = {}
    if current_user and visible:
        pairs = {(c.user_id, c.id) for (c, _) in visible}
        targets = {pair[0] for pair in pairs}
        course_ids = {pair[1] for pair in pairs}
        existing = (
            db.query(ContactRequest)
            .filter(
                ContactRequest.requester_id == current_user.id,
                ContactRequest.target_id.in_(targets),
                ContactRequest.course_id.in_(course_ids),
            )
            .all()
        )
        for req in existing:
            request_map[(req.target_id, req.course_id)] = req

    grouped: dict[tuple[str, str], list[CoursePersonOut]] = {}
    for course, user in visible:
        request = request_map.get((user.id, course.id))
        profile = profile_map.get(user.id)
        university = None
        if profile and isinstance(profile.university_names, list) and profile.university_names:
            university = str(profile.university_names[0])
        if not university:
            university = edu_map.get(user.id)
        if not university:
            university = "Unknown University"
        can_request = (
            current_user is not None
            and user.id != current_user.id
            and course.visibility == "PUBLIC"
            and (request is None or request.status == "IGNORED")
        )
        key = (course.course_number, course.course_name)
        grouped.setdefault(key, []).append(
            CoursePersonOut(
                user_id=user.id,
                name=user.full_name,
                username=user.username,
                university=university,
                course_id=course.id,
                program_level=course.program_level,
                grade=course.grade,
                professor=course.professor,
                term=course.term,
                can_request_contact=can_request,
                request_status=request.status if request else None,
                request_id=request.id if request else None,
            )
        )

    response = []
    for (course_number, course_name), people in grouped.items():
        response.append(
            CourseSearchGroup(
                course_number=course_number,
                course_name=course_name,
                people=people,
            )
        )
    return response

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


PROGRAM_LEVELS = {"BACHELORS", "MASTERS", "PHD", "OTHER"}
VISIBILITY_LEVELS = {"PUBLIC", "CIRCLE", "PRIVATE"}


class CourseCreate(BaseModel):
    course_name: str = Field(..., min_length=2)
    course_number: str = Field(..., min_length=2)
    professor: Optional[str] = None
    grade: str = Field(..., min_length=1)
    program_level: str
    term: Optional[str] = None
    visibility: str = "PUBLIC"


class CourseOut(BaseModel):
    id: UUID
    user_id: int
    course_name: str
    course_number: str
    professor: Optional[str] = None
    grade: str
    program_level: str
    term: Optional[str] = None
    visibility: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CoursePersonOut(BaseModel):
    user_id: int
    name: str
    username: Optional[str] = None
    university: Optional[str] = None
    course_id: UUID
    program_level: str
    grade: str
    professor: Optional[str] = None
    term: Optional[str] = None
    can_request_contact: bool
    request_status: Optional[str] = None
    request_id: Optional[UUID] = None


class CourseSearchGroup(BaseModel):
    course_number: str
    course_name: str
    people: List[CoursePersonOut]

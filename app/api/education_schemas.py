from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime

class EducationCreate(BaseModel):
    degree_type: str
    college_id: str
    gpa: float
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_completed: bool = False

    # verification contact (required)
    advisor_name: str = Field(..., min_length=2, max_length=120)
    advisor_email: EmailStr
    advisor_phone: Optional[str] = Field(None, max_length=40)

class EducationOut(BaseModel):
    id: int
    user_id: int
    degree_type: str
    college_id: str
    university_name: str
    university_tier: int
    gpa: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_completed: bool

    verification_status: str
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True

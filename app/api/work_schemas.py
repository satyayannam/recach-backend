from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime


class WorkCreate(BaseModel):
    company_name: str
    title: str
    employment_type: str
    is_current: bool = False
    start_date: date
    end_date: Optional[date] = None

    # REQUIRED for verification request creation
    supervisor_name: str = Field(..., min_length=2, max_length=120)
    supervisor_email: EmailStr
    supervisor_phone: Optional[str] = Field(None, max_length=40)

    # OPTIONAL extra contact
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None


class WorkOut(BaseModel):
    id: int
    user_id: int

    company_name: str
    title: str
    employment_type: str
    is_current: bool
    start_date: date
    end_date: Optional[date] = None

    verification_status: str
    verified_at: Optional[datetime] = None


    class Config:
        from_attributes = True

from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime

SubjectType = Literal["EDUCATION", "WORK"]
StatusType = Literal["PENDING", "VERIFIED", "REJECTED"]


class VerificationRequestOut(BaseModel):
    id: int
    owner_user_id: int
    subject_type: SubjectType
    subject_id: int
    status: StatusType

    contact_name: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None

    created_at: datetime
    decided_at: Optional[datetime] = None
    decided_by_user_id: Optional[int] = None
    admin_notes: Optional[str] = None

    class Config:
        from_attributes = True


class VerificationDecisionIn(BaseModel):
    admin_notes: Optional[str] = None

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


CONTACT_METHODS = {
    "INSTAGRAM",
    "PHONE",
    "EMAIL",
    "LINKEDIN",
    "DISCORD",
    "TELEGRAM",
    "WHATSAPP",
    "OTHER",
}


class ContactMethodIn(BaseModel):
    method: str = Field(..., min_length=2)
    value: str = Field(..., min_length=2)


class ContactMethodOut(ContactMethodIn):
    id: UUID
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactRequestIn(BaseModel):
    target_id: int
    course_id: UUID
    message: Optional[str] = None


class ContactRequestOut(BaseModel):
    id: UUID
    requester_id: int
    target_id: int
    course_id: UUID
    status: str
    message: Optional[str] = None
    created_at: datetime
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContactRevealOut(BaseModel):
    method: str
    value: str

from datetime import datetime
from pydantic import BaseModel, EmailStr
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    username: str 


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    status: str
    approved_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True

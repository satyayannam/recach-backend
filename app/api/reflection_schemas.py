from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class ReflectionCreate(BaseModel):
    type: str
    content: str = Field(min_length=20)


class ReflectionUserOut(BaseModel):
    id: int
    username: str
    full_name: str
    university: Optional[str] = None


class ReflectionOut(BaseModel):
    id: int
    type: str
    content: str
    created_at: datetime
    user: ReflectionUserOut

    class Config:
        from_attributes = True

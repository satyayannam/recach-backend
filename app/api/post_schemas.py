from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class PostCreate(BaseModel):
    type: str
    content: str = Field(min_length=20)


class PostUserOut(BaseModel):
    id: int
    username: str
    full_name: str
    university: Optional[str] = None
    profile_photo_url: Optional[str] = None


class PostOut(BaseModel):
    id: int
    type: str
    content: str
    created_at: datetime
    user: PostUserOut
    caret_count: int = 0
    has_caret: bool = False

    class Config:
        from_attributes = True


class PostCaretOut(BaseModel):
    post_id: int
    caret_count: int
    has_caret: bool


class CaretUserOut(BaseModel):
    id: int
    username: str
    full_name: str
    profile_photo_url: Optional[str] = None


class CaretNotificationOut(BaseModel):
    id: int
    post_id: int
    post_type: str
    post_content: str
    caret_count: int
    created_at: datetime
    giver: CaretUserOut

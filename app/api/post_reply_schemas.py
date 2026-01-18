from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


PostReplyTypeLiteral = Literal["validate", "context", "impact", "clarify", "challenge"]
PostReplyReactionLiteral = Literal["thanks", "helpful", "noted", "appreciate"]


class PostReplyCreate(BaseModel):
    type: PostReplyTypeLiteral
    message: str = Field(min_length=1, max_length=500)
    recipient_id: Optional[int] = None


class PostReplyUserOut(BaseModel):
    id: int
    username: str
    full_name: str
    profile_photo_url: Optional[str] = None


class PostReplyOut(BaseModel):
    id: int
    post_id: int
    owner_id: int
    sender_id: int
    recipient_id: int
    type: PostReplyTypeLiteral
    message: str
    created_at: datetime
    sender: PostReplyUserOut
    caret_given: bool = False
    owner_reaction: Optional[PostReplyReactionLiteral] = None


class PostReplyCaretOut(BaseModel):
    reply_id: int
    is_given: bool


class PostReplyOwnerReactionIn(BaseModel):
    reaction: PostReplyReactionLiteral


class PostReplyOwnerReactionOut(BaseModel):
    id: int
    reply_id: int
    post_owner_id: int
    reaction: PostReplyReactionLiteral
    created_at: datetime


class InboxPostReplyOut(BaseModel):
    id: int
    reply_type: PostReplyTypeLiteral
    message: str
    created_at: datetime
    sender: PostReplyUserOut
    caret_given: bool = False
    owner_reaction: Optional[PostReplyReactionLiteral] = None


class InboxPostCardOut(BaseModel):
    post_id: int
    post_type: str
    post_content: str
    post_created_at: datetime
    replies: list[InboxPostReplyOut]

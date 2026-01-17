from datetime import datetime
from typing import Any, Dict
from uuid import UUID
from pydantic import BaseModel


class InboxItemOut(BaseModel):
    id: UUID
    type: str
    status: str
    payload_json: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

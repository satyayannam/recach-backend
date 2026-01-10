# app/api/public_profile_schemas.py
from pydantic import BaseModel
from typing import Optional, List


class PublicUserSearchOut(BaseModel):
    user_id: int
    full_name: str
    username: str
    headline: Optional[str] = None
    achievement_total: int
    recommendation_total: int

class RecommenderMini(BaseModel):
    full_name: str
    username: str

class PublicUserOut(BaseModel):
    id: int
    full_name: str
    username: str
    recommended_by: List[RecommenderMini] = []

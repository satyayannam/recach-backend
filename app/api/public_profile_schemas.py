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
    profile_photo_url: Optional[str] = None

class RecommenderMini(BaseModel):
    full_name: str
    username: str

class PublicUserOut(BaseModel):
    id: int
    full_name: str
    username: str
    recommended_by: List[RecommenderMini] = []
    recommender_count: int = 0
    profile_photo_url: Optional[str] = None

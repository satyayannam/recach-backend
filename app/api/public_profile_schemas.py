# app/api/public_profile_schemas.py
from pydantic import BaseModel
from typing import Optional, List


class VerifiedEducation(BaseModel):
    university_name: str
    degree_type: str


class VerifiedWork(BaseModel):
    company_name: str
    title: str


class PublicUserSearchOut(BaseModel):
    user_id: int
    full_name: str
    username: str
    headline: Optional[str] = None
    achievement_total: int
    recommendation_total: int
    caret_score: Optional[int] = None
    verified_education: List[VerifiedEducation] = []
    verified_work: List[VerifiedWork] = []
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
    achievement_total: Optional[int] = None
    recommendation_total: Optional[int] = None
    caret_score: Optional[int] = None
    verified_education: List[VerifiedEducation] = []
    verified_work: List[VerifiedWork] = []

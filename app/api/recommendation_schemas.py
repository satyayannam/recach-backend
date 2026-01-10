from pydantic import BaseModel, Field
from typing import Optional


class RecommendationRequestIn(BaseModel):
    recommender_username: str = Field(..., description="^username or username of recommender")
    rec_type: str
    reason: str = Field(..., max_length=500)



class RecommendationOut(BaseModel):
    id: int
    requester_id: int
    recommender_id: int
    rec_type: str
    reason: str
    note_title: str | None = None
    note_body: str | None = None
    status: str

    class Config:
        from_attributes = True

class RecommendationApproveIn(BaseModel):
    note_title: Optional[str] = Field(None, max_length=120)
    note_body: Optional[str] = None
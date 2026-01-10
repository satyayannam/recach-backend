from pydantic import BaseModel


class RecommendationApprove(BaseModel):
    note_title: str
    note_body: str

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal


Visibility = Literal["PUBLIC", "ONLY_CONNECTIONS", "PRIVATE"]


class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    headline: Optional[str] = Field(default=None, max_length=140)
    about: Optional[str] = None
    profile_photo_url: Optional[str] = Field(default=None, max_length=255)

    location: Optional[str] = Field(default=None, max_length=120)
    pronouns: Optional[str] = Field(default=None, max_length=40)
    website_url: Optional[str] = Field(default=None, max_length=255)

    github_url: Optional[str] = Field(default=None, max_length=255)
    linkedin_url: Optional[str] = Field(default=None, max_length=255)
    portfolio_url: Optional[str] = Field(default=None, max_length=255)
    twitter_url: Optional[str] = Field(default=None, max_length=255)

    interests: Optional[List[Any]] = None
    favorite_movie_character: Optional[str] = Field(default=None, max_length=120)
    favorite_quote: Optional[str] = Field(default=None, max_length=200)

    current_project: Optional[str] = Field(default=None, max_length=200)
    current_goal: Optional[str] = Field(default=None, max_length=200)
    open_to_roles: Optional[List[Any]] = None

    university_names: Optional[List[Any]] = None
    current_semester: Optional[str] = Field(default=None, max_length=30)
    current_courses: Optional[List[Dict[str, Any]]] = None
    clubs: Optional[List[Any]] = None

    top_skills: Optional[List[Any]] = None
    tools_stack: Optional[List[Any]] = None

    is_open_to_recommendations: Optional[bool] = None
    is_hiring: Optional[bool] = None

    favorite_books: Optional[List[Any]] = None
    achievements_highlight: Optional[List[Any]] = None

    visibility: Optional[Visibility] = None

    class Config:
        extra = "forbid"


class UserProfileOut(UserProfileUpdate):
    id: int
    user_id: int
    visibility: Visibility  # ensure returned even if not provided in update
    email: Optional[str] = None
    full_name: Optional[str] = None

    class Config:
        from_attributes = True

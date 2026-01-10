from sqlalchemy import String, Integer, ForeignKey, JSON, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True, nullable=False)

    # ---- Identity / public-facing ----
    headline: Mapped[str | None] = mapped_column(String(140), nullable=True)   # "MS Data Science @ FAU | NLP | Healthcare"
    about: Mapped[str | None] = mapped_column(Text, nullable=True)

    location: Mapped[str | None] = mapped_column(String(120), nullable=True)   # "Boca Raton, FL"
    pronouns: Mapped[str | None] = mapped_column(String(40), nullable=True)    # optional
    website_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ---- Social links ----
    github_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ---- Interests / identity signals ----
    interests: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # ex: ["ML", "Healthcare", "MLOps", "Startups"]

    favorite_movie_character: Mapped[str | None] = mapped_column(String(120), nullable=True)
    favorite_quote: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # ---- Current focus ----
    current_project: Mapped[str | None] = mapped_column(String(200), nullable=True)
    current_goal: Mapped[str | None] = mapped_column(String(200), nullable=True)  # "Looking for Summer 2026 ML internship"
    open_to_roles: Mapped[list | None] = mapped_column(JSON, nullable=True)       # ["Data Analyst", "ML Intern"]

    # ---- University snapshot (display) ----
    university_names: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # ex: ["Florida Atlantic University"]

    current_semester: Mapped[str | None] = mapped_column(String(30), nullable=True)  # "Spring 2026"
    current_courses: Mapped[list | None] = mapped_column(JSON, nullable=True)
    """
    Example:
    [
      {"course_number":"IDS 3949","title":"Career Development","professor":"Dr. X"},
      {"course_number":"CAP 5610","title":"Machine Learning","professor":"Dr. Y"}
    ]
    """

    clubs: Mapped[list | None] = mapped_column(JSON, nullable=True)  # ["IEEE", "DS Club"]

    # ---- Skills snapshot (UI-friendly, not the “true” scored achievements) ----
    top_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # ex: ["Python", "SQL", "FastAPI", "PostgreSQL", "Docker", "Streamlit"]

    tools_stack: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # ex: ["AWS", "GCP", "n8n", "Power BI"]

    # ---- Public proof / verification hints ----
    # (Later you can drive trust badges from these)
    is_open_to_recommendations: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_hiring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ---- Fun / engagement (makes profile “interesting”) ----
    favorite_books: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # ex: ["Deep Work", "Designing Data-Intensive Applications"]

    achievements_highlight: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # ex: ["Published 2 papers", "Built Nurse360 dashboard", "Won Hackathon X"]

    # ---- Privacy controls (so users feel safe using it) ----
    visibility: Mapped[str] = mapped_column(String(20), default="PUBLIC", nullable=False)
    # "PUBLIC" | "ONLY_CONNECTIONS" | "PRIVATE"

    twitter_url: Mapped[str | None] = mapped_column(String(255), nullable=True)


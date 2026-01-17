from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.db.user_profile import UserProfile
from app.db.work_experience import WorkExperience  # noqa: F401
from app.db.recommendations import Recommendation  # noqa: F401
from app.db.education import EducationEntry  # noqa: F401
from app.db.reflection import Reflection  # noqa: F401
from app.db.reflection_caret import ReflectionCaret  # noqa: F401
from app.db.post import Post  # noqa: F401
from app.db.post_caret import PostCaret  # noqa: F401
from app.db.user_course import UserCourse  # noqa: F401
from app.db.contact_method import ContactMethod  # noqa: F401
from app.db.contact_request import ContactRequest  # noqa: F401
from app.db.inbox_item import InboxItem  # noqa: F401
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    google_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=True)  # nullable for migration


    


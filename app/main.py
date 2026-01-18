from fastapi import FastAPI

from app.db.session import engine
from app.db.base import Base
from app.db import models  # noqa: F401  # ensures all models are registered
from app.api.recommendation_score import router as recommendation_score_router

from app.api.users import router as users_router
from app.api.education import router as education_router
from app.api.education_score import router as education_score_router
from app.api.achievement import router as achievement_router
from app.api.work import router as work_router
from app.api.work_score import router as work_score_router
from app.api.recommendations import router as recommendations_router
from app.api.user_profile import router as user_profile_router
from app.api.auth import router as auth_router
from app.api.public_profiles import router as public_profiles_router
from app.api.admin_verifications import router as admin_verifications_router
from app.api.admin_auth import router as admin_auth_router
from app.api.feed import router as feed_router
from app.api.leaderboard import router as leaderboard_router
from app.api.reflections import router as reflections_router
from app.api.posts import router as posts_router
from app.api.courses import router as courses_router
from app.api.contact_methods import router as contact_methods_router
from app.api.contact_requests import router as contact_requests_router
from app.api.inbox import router as inbox_router, posts_router as inbox_posts_router
from app.api.post_replies import router as post_replies_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os


app = FastAPI(title="Recach API", version="0.1.0")


@app.on_event("startup")
def on_startup():
    # Create tables on startup (MVP only)
    Base.metadata.create_all(bind=engine)


# Routers
app.include_router(users_router)
app.include_router(education_router)
app.include_router(education_score_router)
app.include_router(achievement_router)
app.include_router(work_router)
app.include_router(work_score_router)
app.include_router(recommendations_router)
app.include_router(recommendation_score_router)
app.include_router(user_profile_router)
app.include_router(auth_router)
app.include_router(public_profiles_router)
app.include_router(admin_verifications_router)
app.include_router(admin_auth_router)
app.include_router(feed_router)
app.include_router(leaderboard_router)
app.include_router(reflections_router)
app.include_router(posts_router)
app.include_router(courses_router)
app.include_router(contact_methods_router)
app.include_router(contact_requests_router)
app.include_router(inbox_router)
app.include_router(inbox_posts_router)
app.include_router(post_replies_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://recach.vercel.app"
    ],
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

media_dir = os.path.join(os.getcwd(), "uploads")
os.makedirs(media_dir, exist_ok=True)
app.mount("/media", StaticFiles(directory=media_dir), name="media")




@app.get("/health")
def health():
    return {"status": "ok"}

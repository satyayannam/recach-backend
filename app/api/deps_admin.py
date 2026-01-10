# app/api/admin_auth.py
import os
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.core.security import verify_password
from app.core import jwt as jwt_utils

router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip().lower()
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "").strip()

class AdminLoginIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def admin_login(payload: AdminLoginIn):
    if not ADMIN_EMAIL or not ADMIN_PASSWORD_HASH:
        raise HTTPException(
            status_code=500,
            detail="Admin env not configured. Set ADMIN_EMAIL and ADMIN_PASSWORD_HASH.",
        )

    email = payload.email.strip().lower()
    if email != ADMIN_EMAIL:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(payload.password, ADMIN_PASSWORD_HASH):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = jwt_utils.create_access_token(subject=f"admin:{email}")
    return {"access_token": token, "token_type": "bearer"}

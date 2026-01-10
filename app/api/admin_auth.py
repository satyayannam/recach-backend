import os
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.security import verify_password, oauth2_scheme
from app.core.jwt import create_access_token, decode_access_token
from app.db.deps import get_db
from app.db.models import User  # only used if you want decided_by_user_id checks, safe to keep

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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin env not configured. Set ADMIN_EMAIL and ADMIN_PASSWORD_HASH.",
        )

    email = payload.email.strip().lower()
    if email != ADMIN_EMAIL:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(payload.password, ADMIN_PASSWORD_HASH):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=f"admin:{email}")
    return {"access_token": token, "token_type": "bearer"}


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> str:
    """
    Returns the admin email if token is valid.
    Token subject format: "admin:<email>"
    """
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if not sub or not isinstance(sub, str) or not sub.startswith("admin:"):
            raise cred_exc

        admin_email = sub.split("admin:", 1)[1].strip().lower()
        if not admin_email or admin_email != ADMIN_EMAIL:
            raise cred_exc

    except (JWTError, ValueError, TypeError):
        raise cred_exc

    return admin_email

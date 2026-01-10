# app/core/admin_auth.py
import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import oauth2_scheme, verify_password
from app.core import jwt as jwt_utils  # your existing core/jwt.py

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip().lower()
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "").strip()

def require_admin_env_configured():
    if not ADMIN_EMAIL or not ADMIN_PASSWORD_HASH:
        raise RuntimeError(
            "Admin env not configured. Set ADMIN_EMAIL and ADMIN_PASSWORD_HASH."
        )

def issue_admin_token(email: str) -> str:
    # Put role=admin in token payload via a custom encode
    # We'll pack role into 'sub' OR add 'role' in payload (recommended).
    # Since your jwt_utils.create_access_token only accepts subject, we'll encode role into subject.
    # subject example: "admin:satya@..."
    return jwt_utils.create_access_token(subject=f"admin:{email}")

def get_current_admin(
    token: str = Depends(oauth2_scheme),
) -> str:
    """
    Returns admin email if token is valid admin token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated as admin",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt_utils.decode_access_token(token)
        sub: Optional[str] = payload.get("sub")
        if not sub or not sub.startswith("admin:"):
            raise credentials_exception
        admin_email = sub.split("admin:", 1)[1].strip().lower()
        if not admin_email:
            raise credentials_exception
        # Must match configured single admin
        require_admin_env_configured()
        if admin_email != ADMIN_EMAIL:
            raise credentials_exception
        return admin_email
    except (JWTError, ValueError):
        raise credentials_exception

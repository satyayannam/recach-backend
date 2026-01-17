from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import os
import json
import urllib.parse
import urllib.request
import urllib.error

from app.core.security import verify_password
from app.core.jwt import create_access_token
from app.core.approval import is_auto_approved_email
from app.db.deps import get_db
from app.db.models import User
from app.services.username import normalize_username

router = APIRouter(prefix="/auth", tags=["auth"])


class GoogleAuthCode(BaseModel):
    code: str


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    identifier = (form_data.username or "").strip()

    # Login by email OR username (supports '^username')
    if "@" in identifier:
        ident_email = identifier.lower()
        user = db.query(User).filter(User.email == ident_email).first()
    else:
        try:
            uname = normalize_username(identifier)  # '^satya' -> 'satya'
        except ValueError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        user = db.query(User).filter(User.username == uname).first()

    if not user or not user.hashed_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(subject=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/google")
def google_auth(payload: GoogleAuthCode, db: Session = Depends(get_db)):
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

    if not client_id or not client_secret or not redirect_uri:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured")

    token_payload = {
        "code": payload.code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    token_request = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=urllib.parse.urlencode(token_payload).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    try:
        with urllib.request.urlopen(token_request) as response:
            token_data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8") if exc.fp else "Unable to exchange code"
        raise HTTPException(status_code=401, detail=detail)
    except Exception:
        raise HTTPException(status_code=401, detail="Unable to exchange code")

    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Missing Google access token")

    userinfo_request = urllib.request.Request(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    try:
        with urllib.request.urlopen(userinfo_request) as response:
            userinfo = json.loads(response.read().decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=401, detail="Unable to fetch Google user info")

    google_id = str(userinfo.get("id") or "")
    email = (userinfo.get("email") or "").strip().lower()
    full_name = (userinfo.get("name") or "").strip() or email.split("@")[0]

    if not google_id or not email:
        raise HTTPException(status_code=400, detail="Missing Google user data")

    user = db.query(User).filter(User.google_id == google_id).first()
    if not user:
        user = db.query(User).filter(User.email == email).first()
        if user and not user.google_id:
            user.google_id = google_id
    if not user:
        base = email.split("@")[0]
        try:
            candidate = normalize_username(base)
        except ValueError:
            candidate = "user"
        username = candidate
        counter = 2
        while db.query(User).filter(User.username == username).first():
            suffix = str(counter)
            username = (candidate[: (32 - len(suffix))] + suffix) if candidate else f"user{suffix}"
            counter += 1

        user = User(
            full_name=full_name,
            email=email,
            username=username,
            hashed_password=None,
            google_id=google_id
        )
        if is_auto_approved_email(email):
            user.status = "APPROVED"
            user.approved_at = datetime.utcnow()
        db.add(user)

    db.commit()
    db.refresh(user)

    recach_token = create_access_token(subject=str(user.id))
    return {"access_token": recach_token, "token_type": "bearer"}

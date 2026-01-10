from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.core.jwt import create_access_token
from app.db.deps import get_db
from app.db.models import User
from app.services.username import normalize_username

router = APIRouter(prefix="/auth", tags=["auth"])


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

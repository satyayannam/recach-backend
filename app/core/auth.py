from fastapi import Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import oauth2_scheme
from app.core.jwt import decode_access_token
from app.db.deps import get_db
from app.db.models import User


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)  # ✅ uses core/jwt.py SECRET_KEY
        sub = payload.get("sub")
        if not sub:
            raise cred_exc
        user_id = int(sub)
    except (JWTError, ValueError, TypeError):
        raise cred_exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise cred_exc
    return user

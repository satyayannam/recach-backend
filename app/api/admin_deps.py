from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.jwt import decode_access_token

admin_oauth2 = OAuth2PasswordBearer(tokenUrl="/admin/auth/login")

def admin_required(token: str = Depends(admin_oauth2)) -> dict:
    try:
        payload = decode_access_token(token)
        sub = payload.get("sub", "")
        if not sub.startswith("admin:"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not an admin token")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

from fastapi import Header, HTTPException, status
import os
from dotenv import load_dotenv

load_dotenv()

def require_admin(x_admin_key: str = Header(...)):
    admin_key = os.getenv("ADMIN_KEY")
    if not admin_key or x_admin_key != admin_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")

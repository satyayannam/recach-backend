import os
from dotenv import load_dotenv

load_dotenv()

def is_auto_approved_email(email: str) -> bool:
    raw = os.getenv("AUTO_APPROVE_DOMAINS", "")
    allowed = {d.strip().lower() for d in raw.split(",") if d.strip()}
    if not allowed:
        return False

    email = email.strip().lower()
    if "@" not in email:
        return False

    domain = email.split("@")[-1]
    return domain in allowed

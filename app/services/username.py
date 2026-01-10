# backend/app/services/username.py
import re

USERNAME_RE = re.compile(r"^[a-z0-9._]{3,32}$")


def normalize_username(raw: str) -> str:
    """
    Accepts:
      - 'satya'
      - '^satya'
      - '  ^Satya  '

    Returns:
      - 'satya'
    """
    if not raw:
        raise ValueError("Username is required")

    s = raw.strip()

    # strip leading ^
    if s.startswith("^"):
        s = s[1:]

    s = s.lower().strip()

    if not USERNAME_RE.fullmatch(s):
        raise ValueError(
            "Invalid username. Use 3–32 chars: lowercase letters, numbers, . or _"
        )

    return s

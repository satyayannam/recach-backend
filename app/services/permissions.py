from fastapi import HTTPException, status


def ensure_post_owner(post_owner_id: int, user_id: int, detail: str) -> None:
    if post_owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def ensure_reply_owner(reply_owner_id: int, user_id: int, detail: str) -> None:
    if reply_owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

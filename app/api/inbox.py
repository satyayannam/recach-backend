from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps_auth import get_current_user
from app.api.inbox_schemas import InboxItemOut
from app.db.deps import get_db
from app.db.inbox_item import InboxItem
from app.db.models import User

router = APIRouter(prefix="/api/inbox", tags=["Inbox"])


@router.get("", response_model=list[InboxItemOut])
def list_inbox(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = (
        db.query(InboxItem)
        .filter(InboxItem.user_id == current_user.id)
        .order_by(InboxItem.created_at.desc())
        .all()
    )
    return items

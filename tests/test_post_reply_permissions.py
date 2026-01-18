import pytest
from fastapi import HTTPException

from app.services.permissions import ensure_post_owner, ensure_reply_owner


def test_list_replies_forbidden_for_non_owner():
    with pytest.raises(HTTPException) as exc:
        ensure_post_owner(1, 2, "Not allowed to view replies")
    assert exc.value.status_code == 403


def test_toggle_caret_forbidden_for_non_owner():
    with pytest.raises(HTTPException) as exc:
        ensure_reply_owner(1, 2, "Not allowed to toggle caret")
    assert exc.value.status_code == 403

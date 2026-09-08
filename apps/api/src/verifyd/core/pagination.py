import base64
import json
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    next_cursor: Optional[str] = None
    total: Optional[int] = None


def encode_cursor(offset: int) -> str:
    payload = json.dumps({"offset": offset})
    return base64.urlsafe_b64encode(payload.encode()).decode()


def decode_cursor(cursor: Optional[str]) -> int:
    if not cursor:
        return 0
    try:
        raw = base64.urlsafe_b64decode(cursor.encode()).decode()
        data = json.loads(raw)
        return data.get("offset", 0)
    except Exception:
        return 0

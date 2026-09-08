from typing import Any, Dict, Optional
from pydantic import BaseModel


class PresignUploadRequest(BaseModel):
    filename: str
    content_type: str
    size_bytes: int


class PresignUploadResponse(BaseModel):
    url: str
    fields: Dict[str, Any] = {}
    file_key: str
    headers: Dict[str, str] = {}

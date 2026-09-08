from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class OrganizationResponse(BaseModel):
    id: str
    name: str
    type: str
    logo_url: Optional[str] = None
    country: str
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

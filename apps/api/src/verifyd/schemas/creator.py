from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CreatorProfileUpdate(BaseModel):
    bio: Optional[str] = None
    primary_language: Optional[str] = None
    niches: Optional[List[str]] = None
    public_id_enabled: Optional[bool] = None


class CreatorProfileResponse(BaseModel):
    id: str
    user_id: str
    handle: str
    bio: Optional[str] = None
    primary_language: str
    niches: List[str]
    is_verified: bool
    public_id_enabled: bool
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CreatorIDResponse(BaseModel):
    handle: str
    full_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool
    pass_rate: float
    campaigns_completed: int
    average_revisions: float
    total_submissions: int
    public_id_enabled: bool
    niches: List[str] = []
    primary_language: str = "en"


class CreatorVisibilityUpdate(BaseModel):
    enabled: bool

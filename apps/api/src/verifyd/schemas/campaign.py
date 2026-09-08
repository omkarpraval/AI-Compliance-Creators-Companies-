from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CampaignCreate(BaseModel):
    name: str
    product_name: str
    description: Optional[str] = None
    starts_on: Optional[date] = None
    ends_on: Optional[date] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    product_name: Optional[str] = None
    description: Optional[str] = None
    starts_on: Optional[date] = None
    ends_on: Optional[date] = None
    status: Optional[str] = None


class CampaignResponse(BaseModel):
    id: str
    org_id: str
    name: str
    product_name: str
    description: Optional[str] = None
    starts_on: Optional[date] = None
    ends_on: Optional[date] = None
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    contract_count: Optional[int] = 0
    submission_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

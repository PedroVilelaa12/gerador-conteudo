from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, HttpUrl

from app.models.company import OnboardingStatus


class CompanyBase(BaseModel):
    name: str
    website: Optional[HttpUrl] = None
    sector: Optional[str] = None


class CompanyCreate(CompanyBase):
    """Schema para criação de empresa."""
    pass


class CompanyRead(CompanyBase):
    id: UUID
    onboarding_status: OnboardingStatus
    profile_json: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True

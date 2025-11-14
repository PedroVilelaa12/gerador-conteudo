import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class OnboardingStatus(str, enum.Enum):
    INCOMPLETE = "incomplete"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Company(Base):
    __tablename__ = "companies"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name = Column(String(255), nullable=False)
    website = Column(String(255), nullable=True)
    sector = Column(String(255), nullable=True)

    onboarding_status = Column(
        Enum(OnboardingStatus),
        nullable=False,
        default=OnboardingStatus.IN_PROGRESS,
    )

    profile_json = Column(JSON, nullable=True)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

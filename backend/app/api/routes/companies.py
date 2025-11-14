from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.company import Company, OnboardingStatus
from app.schemas.company import CompanyCreate, CompanyRead

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post(
    "",
    response_model=CompanyRead,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    data: CompanyCreate,
    db: Session = Depends(get_db),
):
    company = Company(
        name=data.name,
        website=str(data.website) if data.website else None,
        sector=data.sector,
        onboarding_status=OnboardingStatus.IN_PROGRESS,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("", response_model=List[CompanyRead])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).order_by(Company.created_at.desc()).all()


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
):
    company = db.query(Company).get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return company

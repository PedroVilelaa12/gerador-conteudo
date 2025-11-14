from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.company import CompanyRead
from app.models.company import Company
from app.services.profile_service import build_company_profile

router = APIRouter(prefix="/companies", tags=["companies-profile"])


@router.post("/{company_id}/profile/generate", response_model=CompanyRead)
def generate_profile(company_id: UUID, db: Session = Depends(get_db)):
    try:
        company = build_company_profile(company_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return company


@router.get("/{company_id}/profile")
def get_profile(company_id: UUID, db: Session = Depends(get_db)):
    company: Company | None = db.query(Company).get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    if not company.profile_json:
        raise HTTPException(status_code=404, detail="Perfil ainda não foi gerado")
    return company.profile_json

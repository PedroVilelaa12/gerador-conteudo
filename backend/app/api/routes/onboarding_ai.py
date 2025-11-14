from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db
from app.models.company import Company, OnboardingStatus
from app.services.onboarding_ai_service import ai_check_if_needs_more
from app.models.qa import Question

router = APIRouter(prefix="/onboarding", tags=["onboarding-ai"])


def get_company(company_id: UUID, db: Session):
    company = db.query(Company).get(company_id)
    if not company:
        raise HTTPException(404, "Empresa não encontrada")
    return company


@router.post("/{company_id}/ai/evaluate")
def ai_evaluate(company_id: UUID, db: Session = Depends(get_db)):
    company = get_company(company_id, db)

    result = ai_check_if_needs_more(company_id, db)

    # Caso precise mais perguntas → criar no banco
    if result["precisa_mais"]:
        existing = db.query(Question).filter_by(company_id=company_id).all()
        max_order = max([q.order_index for q in existing], default=0)

        for idx, pergunta in enumerate(result["novas_perguntas"], start=1):
            db.add(
                Question(
                    company_id=company_id,
                    content=pergunta,
                    order_index=max_order + idx,
                    origin="ai",
                )
            )
        company.onboarding_status = OnboardingStatus.IN_PROGRESS
        db.commit()

        return {
            "status": "new_questions_created",
            "novas_perguntas": result["novas_perguntas"]
        }

    # Caso NÃO precise mais → onboarding pode ser finalizado
    return {
        "status": "sufficient",
        "precisa_mais": False
    }

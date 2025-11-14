from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db
from app.schemas.qa import QuestionRead, AnswerCreate, AnswerRead
from app.services.qa_service import (
    start_onboarding,
    get_next_question,
    save_answer,
    check_onboarding_complete,
)
from app.models.company import Company

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


def get_company(company_id: UUID, db: Session):
    company = db.query(Company).get(company_id)
    if not company:
        raise HTTPException(404, "Empresa não encontrada")
    return company


@router.post("/{company_id}/start")
def start(company_id: UUID, db: Session = Depends(get_db)):
    company = get_company(company_id, db)
    start_onboarding(company, db)
    return {"status": "ok"}


@router.get("/{company_id}/next", response_model=QuestionRead)
def next_question(company_id: UUID, db: Session = Depends(get_db)):
    q = get_next_question(company_id, db)
    if not q:
        raise HTTPException(404, "Nenhuma pergunta pendente")
    return q


@router.post("/{company_id}/answer", response_model=AnswerRead)
def answer(
    company_id: UUID,
    data: AnswerCreate,
    db: Session = Depends(get_db),
):
    # valida empresa
    get_company(company_id, db)

    ans = save_answer(
        company_id=str(company_id),
        question_id=str(data.question_id),
        content=data.content,
        db=db,
    )

    check_onboarding_complete(company_id, db)

    return ans

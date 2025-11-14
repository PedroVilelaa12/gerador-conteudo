from sqlalchemy.orm import Session

from app.models.qa import Question, Answer
from app.models.company import Company, OnboardingStatus


# Perguntas fixas obrigatórias
MANDATORY_QUESTIONS = [
    "Qual é o setor/mercado da empresa?",
    "Quem é o público-alvo principal?",
    "Qual é o tom da comunicação desejado (formal, técnico, descontraído...)?",
    "Em quais canais a empresa costuma postar conteúdo?",
    "Quais temas principais são relevantes para a empresa?",
    "Quais temas devem ser evitados pela empresa?",
]


def start_onboarding(company: Company, db: Session):
    """
    Cria as perguntas fixas se elas ainda não existirem.
    """
    existing = db.query(Question).filter_by(company_id=company.id).all()
    if existing:
        return existing

    for idx, q in enumerate(MANDATORY_QUESTIONS, start=1):
        db.add(
            Question(
                company_id=company.id,
                content=q,
                order_index=idx,
                origin="system",
            )
        )
    db.commit()


def get_next_question(company_id: str, db: Session):
    """
    Retorna a próxima pergunta sem resposta.
    """
    # busca todas as perguntas
    questions = (
        db.query(Question)
        .filter(Question.company_id == company_id)
        .order_by(Question.order_index.asc())
        .all()
    )

    if not questions:
        return None

    for q in questions:
        answered = (
            db.query(Answer)
            .filter(
                Answer.company_id == company_id,
                Answer.question_id == q.id,
            )
            .first()
        )
        if not answered:
            return q

    return None  # onboarding finalizado


def save_answer(company_id: str, question_id: str, content: str, db: Session):
    """
    Salva resposta de pergunta.
    """
    ans = Answer(
        company_id=company_id,
        question_id=question_id,
        content=content,
    )
    db.add(ans)
    db.commit()
    db.refresh(ans)
    return ans


def check_onboarding_complete(company_id: str, db: Session):
    """
    Marca empresa como COMPLETED quando todas perguntas obrigatórias forem respondidas.
    """
    company = db.query(Company).get(company_id)

    last_question = (
        db.query(Question)
        .filter_by(company_id=company_id)
        .order_by(Question.order_index.desc())
        .first()
    )

    if not last_question:
        return

    total_questions = last_question.order_index

    answered_count = (
        db.query(Answer)
        .filter(Answer.company_id == company_id)
        .count()
    )

    if answered_count >= total_questions:
        company.onboarding_status = OnboardingStatus.IN_PROGRESS  # depois vira COMPLETED com IA
        db.commit()

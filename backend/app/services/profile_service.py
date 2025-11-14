import json
import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.company import Company, OnboardingStatus
from app.models.qa import Question, Answer
from app.services.ollama_client import chat_ollama
from app.core.prompts import build_company_profile_prompt

logger = logging.getLogger(__name__)


def _extract_json_object(content: str) -> str | None:
    """
    Recorta do primeiro '{' até o último '}'.
    Ignora qualquer lixo antes/depois (markdown, logs, etc).
    """
    if content is None:
        return None

    text = content.strip()

    # remove fences tipo ```json ... ```
    if text.startswith("```"):
        # remove a primeira linha (```json ou ```)
        lines = text.splitlines()
        # tira linha inicial e, se tiver, a última com ```
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    return text[start : end + 1]


def _parse_ai_json_safely(content: str):
    """
    Tenta json.loads normalmente; se falhar, tenta extrair o ÚLTIMO
    bloco JSON do texto (o último {...}) e parsear só ele.
    Se nada funcionar, loga o conteúdo e retorna None.
    """
    content = content.strip()

    # 1) Tenta direto
    try:
        return json.loads(content)
    except Exception:
        pass

    # 2) Tenta pegar APENAS o último objeto JSON
    last_open = content.rfind("{")
    last_close = content.rfind("}")
    if last_open != -1 and last_close != -1 and last_close > last_open:
        candidate = content[last_open:last_close + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    # 3) Se ainda falhar, loga tudo pra debug
    logger.error(
        "Falha ao parsear JSON da IA. Conteúdo bruto:\n%s",
        content,
    )
    return None


def build_company_profile(company_id: UUID, db: Session) -> Company:
    """
    Gera (ou atualiza) o profile_json da empresa a partir das respostas do onboarding.
    Se a resposta da IA vier inválida, NÃO quebra a API: mantém o profile_json anterior.
    """
    company: Company | None = db.query(Company).get(company_id)
    if not company:
        raise ValueError("Empresa não encontrada")

    rows = (
        db.query(Question, Answer)
        .join(Answer, Answer.question_id == Question.id)
        .filter(Question.company_id == company_id)
        .order_by(Question.order_index.asc())
        .all()
    )

    if not rows:
        raise ValueError("Empresa ainda não respondeu perguntas de onboarding")

    qa_pairs = [
        {"pergunta": q.content, "resposta": a.content}
        for (q, a) in rows
    ]

    prompt = build_company_profile_prompt(qa_pairs)
    content = chat_ollama(prompt)

    profile = _parse_ai_json_safely(content)

    if profile is None or not isinstance(profile, dict):
        # Não sobrescreve o profile_json antigo, só loga e segue.
        logger.warning(
            "Usando fallback de profile_json para company_id=%s; resposta IA inválida.",
            company_id,
        )
        # mantém o que já tinha (pode ser None mesmo)
        return company

    # Se chegou aqui, deu bom: salva o profile novo
    company.profile_json = profile
    company.onboarding_status = OnboardingStatus.COMPLETED

    db.add(company)
    db.commit()
    db.refresh(company)

    return company

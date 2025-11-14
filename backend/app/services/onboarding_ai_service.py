# app/services/onboarding_ai_service.py

import json
import logging
from uuid import UUID
from typing import Mapping, Iterable

from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.qa import Question, Answer
from app.services.ollama_client import chat_ollama
from app.core.prompts import build_onboarding_evaluator_prompt

logger = logging.getLogger(__name__)

QaPair = Mapping[str, str]

# 🔹 As 6 perguntas obrigatórias, na ordem:
MANDATORY_QUESTIONS = [
    "Qual é o setor/mercado da empresa?",
    "Quem é o público-alvo principal?",
    "Qual é o tom da comunicação desejado (formal, técnico, descontraído...)?",
    "Em quais canais a empresa costuma postar conteúdo?",
    "Quais temas principais são relevantes para a empresa?",
    "Quais temas devem ser evitados pela empresa?",
]


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


def _get_qa_pairs(company_id: UUID, db: Session) -> list[QaPair]:
    """
    Busca todas as perguntas e respostas dessa empresa, já ordenadas.
    """
    rows = (
        db.query(Question, Answer)
        .join(Answer, Answer.question_id == Question.id)
        .filter(Question.company_id == company_id)
        .order_by(Question.order_index.asc())
        .all()
    )

    return [
        {"pergunta": q.content, "resposta": a.content}
        for (q, a) in rows
    ]


def ai_check_if_needs_more(company_id: UUID, db: Session) -> dict:
    """
    Decide se:
      - ainda estamos na fase das 6 perguntas obrigatórias (sem IA), ou
      - já podemos chamar a IA para perguntas complementares.

    Retorna sempre:
    {
        "precisa_mais": bool,
        "novas_perguntas": [str, ...]
    }
    """
    company: Company | None = db.query(Company).get(company_id)
    if not company:
        raise ValueError("Empresa não encontrada")

    qa_pairs = _get_qa_pairs(company_id, db)
    qtd = len(qa_pairs)

    # 1) ENQUANTO NÃO TIVER AS 6 BÁSICAS, NÃO CHAMA IA
    if qtd < len(MANDATORY_QUESTIONS):
        proxima_pergunta = MANDATORY_QUESTIONS[qtd]  # índice 0..5
        return {
            "precisa_mais": True,
            "novas_perguntas": [proxima_pergunta],
        }

    # 2) JÁ TEM AS 6 BÁSICAS → AGORA SIM CHAMA A IA AVALIADORA
    prompt = build_onboarding_evaluator_prompt(qa_pairs)

    try:
        content = chat_ollama(prompt)
    except Exception as e:
        logger.error("Erro ao chamar Ollama na avaliação de onboarding: %r", e)
        # Fallback: não trava o fluxo → considera que já é suficiente
        return {
            "precisa_mais": False,
            "novas_perguntas": [],
        }

    obj = _parse_ai_json_safely(content)
    if obj is None or not isinstance(obj, dict):
        logger.warning(
            "IA retornou JSON inválido, aplicando fallback (precisa_mais = false)."
        )
        return {
            "precisa_mais": False,
            "novas_perguntas": [],
        }

    precisa_mais = bool(obj.get("precisa_mais", False))
    novas_perguntas = obj.get("novas_perguntas") or []

    if not isinstance(novas_perguntas, list):
        novas_perguntas = []

    novas_perguntas = [str(p).strip() for p in novas_perguntas if str(p).strip()]

    # Se, por acaso, a IA mandar muitas perguntas, limita a no máximo 2
    if precisa_mais and len(novas_perguntas) > 2:
        novas_perguntas = novas_perguntas[:2]

    return {
        "precisa_mais": precisa_mais,
        "novas_perguntas": novas_perguntas,
    }

import logging
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def chat_ollama(prompt: str, model: str | None = None, timeout: float = 300.0) -> str:
    """
    Envia um prompt para o Ollama e retorna o conteúdo da resposta (string).

    Usa o endpoint /api/generate (compatível com versões que não têm /api/chat).
    """
    model = model or getattr(settings, "OLLAMA_MODEL", "llama3")
    base_url = getattr(settings, "OLLAMA_BASE_URL", "http://curadoria-ollama:11434")
    url = f"{base_url}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
    except httpx.ReadTimeout:
        logger.error("Timeout ao chamar Ollama em %s", url)
        raise
    except httpx.HTTPError as e:
        logger.error("Erro HTTP ao chamar Ollama: %r", e)
        raise

    data = resp.json()

    # Formato padrão do /api/generate: {"response": "...", ...}
    if isinstance(data, dict) and "response" in data:
        return str(data["response"]).strip()

    # Se vier em outro formato, devolve bruto mesmo
    return str(data).strip()

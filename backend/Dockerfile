FROM python:3.13-slim

# Evita prompt interativo
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

# Instala dependências do sistema (psycopg2 precisa de libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN pip install poetry

# Copia somente configs do Poetry primeiro (melhora cache)
COPY pyproject.toml poetry.lock* ./

# Instala dependências
RUN poetry install --no-root

# Agora copia o resto do código
COPY . .

# Porta da API
EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

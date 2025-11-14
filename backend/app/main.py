from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.routes import companies as companies_router
from app.api.routes import onboarding as onboarding_router
from app.api.routes import profile as profile_router
from app.models import company, qa
from app.api.routes import onboarding_ai as onboarding_ai_router


# Cria as tabelas (para começar simples; depois dá pra usar Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

# CORS pra falar com o frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # libera geral em dev
    allow_credentials=False,  # tem que ser False se usar "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    companies_router.router,
    prefix=settings.API_PREFIX,
)

app.include_router(
    onboarding_router.router,
    prefix=settings.API_PREFIX,
)

app.include_router(
    profile_router.router,
    prefix=settings.API_PREFIX,
)

app.include_router(
    onboarding_ai_router.router,
    prefix=settings.API_PREFIX,
)

@app.get("/")
def healthcheck():
    return {"status": "ok"}

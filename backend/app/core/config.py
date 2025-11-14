from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    OLLAMA_BASE_URL: str = "http://ollama:11434"

    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "Painel de Curadoria"

    class Config:
        env_file = ".env"


settings = Settings()

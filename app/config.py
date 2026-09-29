from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings powered by Pydantic v2 BaseSettings.
    Automatically reads environment variables and enforces strict typing.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = "FastAPI Open LLM Microservice"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Security & JWT Authentication
    SECRET_KEY: str = Field(
        default="super-secret-jwt-key-change-in-production-environment",
        description="JWT Signing secret key"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Model Provider Settings
    LLM_BACKEND: Literal["local_mock", "ollama", "huggingface", "openrouter"] = "local_mock"
    DEFAULT_MODEL: str = "llama3-open-8b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    HUGGINGFACE_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""

    # AI Rate Limiting & Usage Controls
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 20
    RATE_LIMIT_TOKENS_PER_MINUTE: int = 10000


settings = Settings()

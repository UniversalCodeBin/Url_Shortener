import importlib
from functools import lru_cache

# Prefer the standalone pydantic-settings package (pydantic v2.12+ moved BaseSettings there).
try:
    BaseSettings = importlib.import_module("pydantic_settings").BaseSettings
except Exception:
    # Older pydantic versions exposed BaseSettings directly; try that for compatibility.
    try:
        BaseSettings = importlib.import_module("pydantic").BaseSettings
    except Exception:
        raise ImportError(
            "BaseSettings import failed. Install 'pydantic-settings' (pip install pydantic-settings) "
            "or run tests using the project's virtual environment where dependencies are installed."
        )


class Settings(BaseSettings):
    APP_NAME: str = "URL Shortener"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    BASE_URL: str = "http://127.0.0.1:8000"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "url_shortener"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()

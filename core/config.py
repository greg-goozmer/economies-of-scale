from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_ENDPOINT: str = "127.0.0.1:9000"
    MINIO_PUBLIC_URL: str = "http://localhost:9000"
    MINIO_BUCKET: str = "costs"
    REDIS_URL: str = "redis://127.0.0.1:16379/0"
    SESSION_COOKIE_NAME: str = "cost_session"
    SESSION_TTL_SECONDS: int = Field(default=3600, gt=0)
    SESSION_COOKIE_SECURE: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def DATABASE_URL(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()

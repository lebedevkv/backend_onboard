from __future__ import annotations
from functools import lru_cache
from typing import List, Any, Annotated
from pydantic import field_validator

from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, Field, AnyHttpUrl


class Settings(BaseSettings):
    # URL подключения к базе данных PostgreSQL
    DATABASE_URL: PostgresDsn = Field(..., env="DATABASE_URL")

    # Параметры JWT
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Host/port для Uvicorn или Docker
    SERVER_HOST: str = Field("0.0.0.0", env="SERVER_HOST")
    SERVER_PORT: int = Field(8000, env="SERVER_PORT")

    # Разрешённые CORS-источники (можно задавать через ENV переменную)
    CORS_ORIGINS: Annotated[
        List[AnyHttpUrl],
        Field(default_factory=list, env="CORS_ORIGINS")
    ]
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Any) -> List[AnyHttpUrl]:
        # Если пришло уже в виде списка — ничего не трогаем
        if isinstance(v, list):
            return v
        # Если строка CSV — разбираем по запятым
        if isinstance(v, str) and v:
            return [url.strip() for url in v.split(",")]
        # Иначе возвращаем пустой список
        return []

    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
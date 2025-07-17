from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env.local"
        extra = "allow"  # позволяет игнорировать лишние поля

@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
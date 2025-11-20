from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "WhatsApp Product Review Collector"
    database_url: str = "postgresql://postgres:postgres@db:5432/reviews"
    twilio_auth_token: str | None = None
    twilio_verify_signatures: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


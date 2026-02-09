from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(default="Credit API")
    api_v1_prefix: str = Field(default="/api/v1")
    api_key: str = Field(default="dev-api-key", description="Static API key for auth")

    database_url: str = Field(
        default="mysql+asyncmy://root:root@db:3306/credits",
        description="Async SQLAlchemy database URL",
    )

    debug: bool = Field(default=True)
    echo_sql: bool = Field(default=False)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache

def get_settings() -> Settings:
    return Settings()

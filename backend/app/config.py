from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Zhuotuan Backend")
    app_env: str = Field(default="local")
    app_debug: bool = Field(default=True)
    api_prefix: str = Field(default="/api")
    api_v1_prefix: str = Field(default="/api/v1")
    llm_provider: str = Field(default="openai_compatible")
    llm_model: str = Field(default="deepseek-v4-flash")
    llm_timeout_seconds: float = Field(default=60.0)
    llm_api_base_url: str | None = Field(default=None)
    llm_chat_completions_path: str = Field(default="/chat/completions")
    llm_api_key: str | None = Field(default=None)
    llm_temperature: float = Field(default=0.7)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and `.env`."""

    app_name: str = Field(default="ProofPath AI", validation_alias="APP_NAME")
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    api_host: str = Field(default="127.0.0.1", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    database_url: str = Field(
        default="sqlite:///./data/proofpath.db",
        validation_alias="DATABASE_URL",
    )
    data_dir: str = Field(default="./data", validation_alias="DATA_DIR")
    report_dir: str = Field(default="./reports", validation_alias="REPORT_DIR")
    search_timeout_seconds: float = Field(default=15.0, validation_alias="SEARCH_TIMEOUT_SECONDS")
    max_search_results: int = Field(default=6, validation_alias="MAX_SEARCH_RESULTS")
    llm_provider: str | None = Field(default=None, validation_alias="LLM_PROVIDER")
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    gemini_api_key: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    tavily_api_key: str | None = Field(default=None, validation_alias="TAVILY_API_KEY")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()

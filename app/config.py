from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

openrouter_base_url: str = "https://openrouter.ai/api/v1"

class Settings(BaseSettings):
    # Telegram
    telegram_token: str

    # AI
    ai_provider: str

    mistral_api_key: str | None = None
    gemini_api_key: str | None = None
    openrouter_api_key: str | None = None

    mistral_model: str
    gemini_model: str
    openrouter_model: str

    # Tools
    openweather_api_key: str | None = None

    # HTTP
    http_timeout: int = 90
    http_retries: int = 3
    http_retry_delay: int = 2

    # Database
    database_path: Path = Path("data/leo.db")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
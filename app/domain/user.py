from datetime import datetime

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    """Участник Telegram."""

    model_config = ConfigDict(
        frozen=False,
        extra="forbid",
        validate_assignment=True,
    )

    telegram_user_id: int

    username: str | None = None

    first_name: str

    last_name: str | None = None

    language_code: str | None = None

    is_bot: bool = False

    created_at: datetime

    updated_at: datetime
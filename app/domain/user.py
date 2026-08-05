from app.domain.base import DomainModel


class User(DomainModel):
    """Пользователь Telegram."""
    telegram_user_id: int
    username: str | None = None
    first_name: str
    last_name: str | None = None
    language_code: str | None = None
    is_bot: bool = False
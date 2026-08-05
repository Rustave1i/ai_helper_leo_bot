from app.domain.base import DomainModel


class Chat(DomainModel):
    """Telegram-чат."""
    telegram_chat_id: int
    type: str
    title: str | None = None
    username: str | None = None
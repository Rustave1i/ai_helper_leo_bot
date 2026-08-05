from app.domain.base import DomainModel


class Message(DomainModel):
    """Сообщение Telegram."""
    telegram_message_id: int
    chat_id: int
    user_id: int
    reply_to_telegram_message_id: int | None = None
    text: str | None = None
    is_deleted: bool = False
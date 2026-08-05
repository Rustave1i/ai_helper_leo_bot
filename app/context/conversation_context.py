from datetime import UTC, datetime

from pydantic import Field

from app.domain.base import DomainModel
from app.domain.chat import Chat
from app.domain.message import Message
from app.domain.user import User


class ConversationContext(DomainModel):
    """Контекст обработки входящего сообщения."""

    chat: Chat

    user: User

    message: Message

    received_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )
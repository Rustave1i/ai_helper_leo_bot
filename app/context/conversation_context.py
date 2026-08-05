from datetime import datetime

from ..domain.base import DomainModel
from ..domain.chat import Chat
from ..domain.message import Message
from ..domain.user import User


class ConversationEvent(DomainModel):
    """Новое сообщение, поступившее в Leo."""

    chat: Chat

    user: User

    message: Message

    received_at: datetime
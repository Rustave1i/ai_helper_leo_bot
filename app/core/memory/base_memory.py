from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.core.models import ConversationKey, Message


class BaseMemory(ABC):
    """Base interface for conversation history storage."""

    @abstractmethod
    def append(
        self,
        key: ConversationKey,
        message: Message,
    ) -> None:
        """Add a conversation message for a key."""

    @abstractmethod
    def history(
        self,
        key: ConversationKey,
        limit: int | None = None,
    ) -> Sequence[Message]:
        """Return oldest-to-newest messages for a key."""

    @abstractmethod
    def clear(self, key: ConversationKey) -> None:
        """Clear one conversation history."""

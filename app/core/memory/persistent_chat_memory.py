from typing import Sequence

from app.core.memory.base_memory import BaseMemory
from app.core.memory.sqlite_conversation_repository import (
    SQLiteConversationRepository,
)
from app.core.models import ConversationKey, Message


class PersistentChatMemory(BaseMemory):
    """Bounded persistent conversation memory backed by SQLite."""

    MAX_MESSAGES = 20

    def __init__(self, repository: SQLiteConversationRepository) -> None:
        self._repository = repository

    def append(self, key: ConversationKey, message: Message) -> None:
        self._repository.append(key, message)
        self._repository.trim(key, self.MAX_MESSAGES)

    def history(
        self,
        key: ConversationKey,
        limit: int | None = None,
    ) -> Sequence[Message]:
        if limit == 0:
            return []

        effective_limit = self.MAX_MESSAGES if limit is None else min(
            limit,
            self.MAX_MESSAGES,
        )
        return self._repository.history(key, effective_limit)

    def clear(self, key: ConversationKey) -> None:
        self._repository.clear(key)
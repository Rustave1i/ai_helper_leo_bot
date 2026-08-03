from collections.abc import Sequence

from app.core.models import Message

from .base_memory import BaseMemory
from .memory_store import MemoryStore


class ChatMemory(BaseMemory):
    """Управляет историей сообщений пользователей."""

    MAX_MESSAGES = 20

    def __init__(self) -> None:

        self._store = MemoryStore()

    def get(
        self,
        user_id: int,
    ) -> Sequence[Message]:

        return self._store.get(user_id)

    def add(
        self,
        user_id: int,
        message: Message,
    ) -> None:

        self._store.add(
            user_id=user_id,
            message=message,
        )

        history = self._store.get(user_id)

        if len(history) > self.MAX_MESSAGES:
            del history[0]

    def clear(
        self,
        user_id: int,
    ) -> None:

        self._store.clear(user_id)
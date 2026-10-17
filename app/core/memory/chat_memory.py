from collections import defaultdict
from typing import Sequence

from app.core.memory.base_memory import BaseMemory
from app.core.models import ConversationKey, Message, Role


class ChatMemory(BaseMemory):
    """Bounded in-memory BaseMemory implementation for tests."""

    MAX_MESSAGES = 20

    def __init__(self) -> None:
        self._history: dict[ConversationKey, list[Message]] = defaultdict(list)

    def append(self, key: ConversationKey, message: Message) -> None:
        if message.role is Role.SYSTEM:
            raise ValueError("System messages are not conversation memory.")

        messages = self._history[key]
        messages.append(message)
        if len(messages) > self.MAX_MESSAGES:
            del messages[0]

    def history(
        self,
        key: ConversationKey,
        limit: int | None = None,
    ) -> Sequence[Message]:
        messages = self._history[key]
        if limit is None:
            return list(messages)
        if limit == 0:
            return []
        return list(messages[-limit:])

    def clear(self, key: ConversationKey) -> None:
        self._history[key].clear()
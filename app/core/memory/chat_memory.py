from collections import defaultdict

from app.core.models import ConversationKey, Message, Role

from .base_memory import BaseMemory


class ChatMemory(BaseMemory):
    """Stores bounded in-memory conversation histories."""

    MAX_MESSAGES = 20

    def __init__(self) -> None:
        self._history: dict[ConversationKey, list[Message]] = defaultdict(list)
        self._legacy_history: dict[int, list[Message]] = defaultdict(list)

    def append(self, key: ConversationKey, message: Message) -> None:
        self._append_to(self._history[key], message)

    def history(
        self,
        key: ConversationKey,
        limit: int | None = None,
    ) -> list[Message]:
        messages = self._history[key]
        if limit is None:
            return list(messages)
        if limit == 0:
            return []
        return list(messages[-limit:])

    def clear(self, key: ConversationKey | int) -> None:
        if isinstance(key, ConversationKey):
            self._history[key].clear()
            return
        self._legacy_history[key].clear()

    def add_message(self, user_id: int, message: Message) -> None:
        """Temporary user-only API retained until ChatEngine gets chat identity."""
        self._append_to(self._legacy_history[user_id], message)

    def get_history(self, user_id: int) -> list[Message]:
        """Temporary user-only API retained until ChatEngine gets chat identity."""
        return list(self._legacy_history[user_id])

    def _append_to(self, messages: list[Message], message: Message) -> None:
        if message.role == Role.SYSTEM:
            raise ValueError("System messages are not conversation memory.")

        messages.append(message)
        if len(messages) > self.MAX_MESSAGES:
            del messages[0]

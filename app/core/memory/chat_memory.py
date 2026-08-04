from collections import defaultdict

from app.core.models import Message

from .base_memory import BaseMemory


class ChatMemory(BaseMemory):
    """Хранит историю переписки пользователей."""

    MAX_MESSAGES = 20

    def __init__(self) -> None:

        self._history: dict[
            int,
            list[Message],
        ] = defaultdict(list)

    def add_message(
        self,
        user_id: int,
        message: Message,
    ) -> None:

        messages = self._history[user_id]

        messages.append(message)

        if len(messages) > self.MAX_MESSAGES:
            del messages[0]

    def get_history(
        self,
        user_id: int,
    ) -> list[Message]:

        return list(
            self._history[user_id]
        )

    def clear(
        self,
        user_id: int,
    ) -> None:

        self._history[user_id].clear()
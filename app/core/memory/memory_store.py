from collections import defaultdict
from collections.abc import Sequence

from app.core.models import Message


class MemoryStore:
    """Хранилище сообщений в оперативной памяти."""

    def __init__(self) -> None:

        self._storage: dict[
            int,
            list[Message],
        ] = defaultdict(list)

    def get(
        self,
        user_id: int,
    ) -> Sequence[Message]:

        return self._storage[user_id]

    def add(
        self,
        user_id: int,
        message: Message,
    ) -> None:

        self._storage[user_id].append(message)

    def clear(
        self,
        user_id: int,
    ) -> None:

        self._storage[user_id].clear()
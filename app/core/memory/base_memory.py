from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.core.models import Message


class BaseMemory(ABC):
    """Базовый интерфейс памяти чата."""

    @abstractmethod
    def get(
        self,
        user_id: int,
    ) -> Sequence[Message]:
        """Возвращает историю сообщений."""
        raise NotImplementedError

    @abstractmethod
    def add(
        self,
        user_id: int,
        message: Message,
    ) -> None:
        """Добавляет сообщение."""
        raise NotImplementedError

    @abstractmethod
    def clear(
        self,
        user_id: int,
    ) -> None:
        """Очищает историю пользователя."""
        raise NotImplementedError
from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.core.models import Message


class BaseMemory(ABC):
    """Базовый интерфейс хранилища истории сообщений."""

    @abstractmethod
    def add_message(
        self,
        user_id: int,
        message: Message,
    ) -> None:
        """Добавляет сообщение в историю."""

    @abstractmethod
    def get_history(
        self,
        user_id: int,
    ) -> Sequence[Message]:
        """Возвращает историю сообщений."""

    @abstractmethod
    def clear(
        self,
        user_id: int,
    ) -> None:
        """Очищает историю пользователя."""
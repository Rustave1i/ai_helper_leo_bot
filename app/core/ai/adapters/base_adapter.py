from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.core.models import Message


class BaseAdapter(ABC):
    """Базовый класс адаптера сообщений."""

    @abstractmethod
    def convert(
        self,
        messages: Sequence[Message],
    ):
        """Преобразует внутренние модели в формат AI."""
        raise NotImplementedError
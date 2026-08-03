from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.core.models import Message


class BaseAdapter(ABC):
    """Базовый адаптер AI-провайдера."""

    @abstractmethod
    def to_provider_format(
        self,
        messages: Sequence[Message],
    ):
        """
        Преобразует внутренние модели
        в формат AI-провайдера.
        """
        raise NotImplementedError

    @abstractmethod
    def from_provider_response(
        self,
        response,
    ) -> str:
        """
        Преобразует ответ AI
        в обычную строку.
        """
        raise NotImplementedError
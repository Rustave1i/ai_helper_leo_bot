from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.core.models import Message


class BaseAIClient(ABC):
    """Базовый интерфейс AI-клиента."""

    @abstractmethod
    def ask(
        self,
        messages: Sequence[Message],
    ) -> str:
        """Отправляет сообщения модели и возвращает ответ."""
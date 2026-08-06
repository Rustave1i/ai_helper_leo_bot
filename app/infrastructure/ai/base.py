from abc import ABC, abstractmethod

from app.infrastructure.ai.models import (
    AIRequest,
    AIResponse,
)


class AIClient(ABC):
    """Базовый интерфейс AI."""

    @abstractmethod
    async def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        """Получить ответ AI."""
        raise NotImplementedError
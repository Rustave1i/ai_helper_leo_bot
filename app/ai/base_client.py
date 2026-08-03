from abc import ABC, abstractmethod


class BaseAIClient(ABC):
    """Базовый интерфейс любого AI-провайдера."""

    @abstractmethod
    def ask(
        self,
        user_id: int,
        message: str,
    ) -> str:
        """Отправить сообщение модели."""
        pass

    @abstractmethod
    def clear_history(
        self,
        user_id: int,
    ) -> None:
        """Очистить историю пользователя."""
        pass
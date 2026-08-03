from abc import ABC, abstractmethod


class BaseAIClient(ABC):
    """Базовый интерфейс любого AI-провайдера."""

    @abstractmethod
    def ask(self, messages: list[dict]) -> str:
        """
        Получает готовую историю сообщений
        и возвращает ответ модели.
        """
        raise NotImplementedError
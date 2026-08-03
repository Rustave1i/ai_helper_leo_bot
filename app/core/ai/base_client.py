from abc import ABC, abstractmethod


class BaseAIClient(ABC):
    """Базовый интерфейс AI-провайдера."""

    @abstractmethod
    def ask(self, messages: list[dict]) -> str:
        """
        Получает историю сообщений и
        возвращает ответ модели.
        """
        raise NotImplementedError
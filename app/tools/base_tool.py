from abc import ABC, abstractmethod


class BaseTool(ABC):
    """Базовый класс любого инструмента."""

    name: str = "tool"

    @abstractmethod
    def can_handle(self, message: str) -> bool:
        """Может ли инструмент обработать сообщение."""
        raise NotImplementedError

    @abstractmethod
    def execute(self, message: str) -> str:
        """Выполнить инструмент."""
        raise NotImplementedError
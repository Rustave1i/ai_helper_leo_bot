from abc import ABC, abstractmethod

from .models.tool_definition import ToolDefinition
from .models.tool_result import ToolResult


class BaseTool(ABC):
    """Базовый класс AI-инструмента."""

    @property
    @abstractmethod
    def definition(
        self,
    ) -> ToolDefinition:
        """Описание инструмента для LLM."""

    @abstractmethod
    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        """Выполняет инструмент."""
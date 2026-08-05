from .base_tool import BaseTool
from .models import (
    ToolCall,
    ToolDefinition,
    ToolResult,
)


class ToolManager:
    """Менеджер AI-инструментов."""

    def __init__(self) -> None:

        self._tools: dict[
            str,
            BaseTool,
        ] = {}

    def register(
        self,
        tool: BaseTool,
    ) -> None:
        """Регистрирует инструмент."""

        self._tools[
            tool.definition.name
        ] = tool

    def definitions(
        self,
    ) -> list[ToolDefinition]:
        """Возвращает описания всех инструментов."""

        return [
            tool.definition
            for tool in self._tools.values()
        ]

    async def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:
        """Выполняет инструмент."""

        tool = self._tools.get(
            call.name
        )

        if tool is None:

            return ToolResult(
                success=False,
                content=(
                    f"Инструмент "
                    f"'{call.name}' "
                    f"не найден."
                ),
            )

        return await tool.execute(
            **call.arguments
        )
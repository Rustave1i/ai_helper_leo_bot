from dataclasses import dataclass


@dataclass(slots=True)
class ToolResult:
    """Результат выполнения инструмента."""

    success: bool

    content: str
from dataclasses import dataclass, field


@dataclass(slots=True)
class ToolCall:
    """Запрос на выполнение инструмента."""

    name: str

    arguments: dict = field(
        default_factory=dict,
    )
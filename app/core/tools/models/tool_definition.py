from dataclasses import dataclass, field


@dataclass(slots=True)
class ToolDefinition:
    """Описание инструмента."""

    name: str

    description: str

    parameters: dict = field(
        default_factory=dict,
    )
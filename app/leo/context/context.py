from dataclasses import dataclass

from app.infrastructure.ai.models import AIMessage


@dataclass(slots=True)
class Context:
    """Контекст, который будет передан в PromptBuilder."""

    system_prompt: str

    messages: list[AIMessage]
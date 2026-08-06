from app.infrastructure.ai.models import (
    AIMessage,
    AIRequest,
)
from app.leo.context.context import Context


class PromptBuilder:
    """Формирует запрос к AI."""

    def build(
        self,
        context: Context,
    ) -> AIRequest:

        return AIRequest(
            messages=[
                AIMessage(
                    role="system",
                    content=context.system_prompt,
                ),
                *context.messages,
            ],
        )
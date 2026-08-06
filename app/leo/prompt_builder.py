from app.context.conversation_context import ConversationContext
from app.infrastructure.ai.models import (
    AIMessage,
    AIRequest,
)
from app.leo.prompt_loader import PromptLoader


class PromptBuilder:
    """Формирует запрос к AI."""

    def __init__(
        self,
        loader: PromptLoader,
    ) -> None:
        self._loader = loader

    def build(
        self,
        context: ConversationContext,
    ) -> AIRequest:

        system_prompt = self._loader.load(
            "assistant.md",
        )

        return AIRequest(
            messages=[
                AIMessage(
                    role="system",
                    content=system_prompt,
                ),
                AIMessage(
                    role="user",
                    content=context.message.text or "",
                ),
            ],
        )
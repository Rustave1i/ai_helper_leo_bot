from app.context.conversation_context import ConversationContext
from app.leo.context.context import Context
from app.leo.context.providers.history_provider import (
    HistoryProvider,
)
from app.leo.prompt_loader import PromptLoader


class ContextEngine:
    """Собирает контекст для AI."""

    def __init__(
        self,
        loader: PromptLoader,
        history_provider: HistoryProvider,
    ) -> None:
        self._loader = loader
        self._history_provider = history_provider

    async def build(
        self,
        conversation: ConversationContext,
    ) -> Context:

        return Context(
            system_prompt=self._loader.load(
                "assistant.md",
            ),
            messages=await self._history_provider.load(
                conversation,
            ),
        )
from app.context.conversation_context import ConversationContext
from app.infrastructure.ai.base import AIClient
from app.infrastructure.ai.models import AIResponse
from app.leo.context.engine import ContextEngine
from app.leo.prompt_builder import PromptBuilder


class Assistant:
    """Главный координатор Leo."""

    def __init__(
        self,
        context_engine: ContextEngine,
        prompt_builder: PromptBuilder,
        ai: AIClient,
    ) -> None:
        self._context_engine = context_engine
        self._prompt_builder = prompt_builder
        self._ai = ai

    async def handle(
        self,
        conversation: ConversationContext,
    ) -> AIResponse | None:

        if not self._is_addressed_to_leo(
            conversation,
        ):
            return None

        context = await self._context_engine.build(
            conversation,
        )

        request = self._prompt_builder.build(
            context,
        )

        return await self._ai.generate(
            request,
        )

    def _is_addressed_to_leo(
        self,
        conversation: ConversationContext,
    ) -> bool:

        if conversation.chat.type == "private":
            return True

        text = (
            conversation.message.text
            or ""
        ).lower()

        return (
            "@ai_helper_leo_bot" in text
            or "@leo" in text
            or "лео" in text
            or "leo" in text
        )
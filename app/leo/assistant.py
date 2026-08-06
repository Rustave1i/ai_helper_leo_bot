from app.context.conversation_context import ConversationContext
from app.infrastructure.ai.base import AIClient
from app.infrastructure.ai.models import AIResponse
from app.leo.prompt_builder import PromptBuilder


class Assistant:
    """Главный координатор Leo."""

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        ai: AIClient,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._ai = ai

    async def handle(
        self,
        context: ConversationContext,
    ) -> AIResponse | None:

        if not self._is_addressed_to_leo(
            context,
        ):
            return None

        request = self._prompt_builder.build(
            context,
        )

        return await self._ai.generate(
            request,
        )

    def _is_addressed_to_leo(
        self,
        context: ConversationContext,
    ) -> bool:

        if context.chat.type == "private":
            return True

        text = (context.message.text or "").lower()

        return (
            "@leo" in text
            or "leo" in text
            or "лео" in text
        )
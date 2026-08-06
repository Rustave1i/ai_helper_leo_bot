from app.context.conversation_context import ConversationContext
from app.domain.system_users import LEO_USER_ID
from app.infrastructure.ai.models import AIMessage
from app.infrastructure.conversation_store import ConversationStore
from app.leo.context.context import Context
from app.leo.prompt_loader import PromptLoader


class ContextEngine:
    """Собирает контекст для AI."""

    def __init__(
        self,
        loader: PromptLoader,
        conversation_store: ConversationStore,
    ) -> None:
        self._loader = loader
        self._conversation_store = conversation_store

    async def build(
        self,
        conversation: ConversationContext,
    ) -> Context:

        history = await self._conversation_store.get_last_messages(
            chat_id=conversation.chat.telegram_chat_id,
            limit=20,
        )

        return Context(
            system_prompt=self._loader.load(
                "assistant.md",
            ),
            messages=[
                AIMessage(
                    role=self._role(
                        message.user_id,
                    ),
                    content=message.text or "",
                )
                for message in history
            ],
        )

    def _role(
        self,
        user_id: int,
    ) -> str:

        if user_id == LEO_USER_ID:
            return "assistant"

        return "user"
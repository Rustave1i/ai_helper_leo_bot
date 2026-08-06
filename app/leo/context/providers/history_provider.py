from app.context.conversation_context import ConversationContext
from app.domain.system_users import LEO_USER_ID
from app.infrastructure.ai.models import AIMessage
from app.infrastructure.conversation_store import ConversationStore


class HistoryProvider:
    """Добавляет историю переписки в контекст."""

    def __init__(
        self,
        conversation_store: ConversationStore,
    ) -> None:
        self._conversation_store = conversation_store

    async def load(
        self,
        conversation: ConversationContext,
    ) -> list[AIMessage]:

        history = await self._conversation_store.get_last_messages(
            chat_id=conversation.chat.telegram_chat_id,
            limit=20,
        )

        return [
            AIMessage(
                role=self._role(
                    message.user_id,
                ),
                content=message.text or "",
            )
            for message in history
        ]

    def _role(
        self,
        user_id: int,
    ) -> str:

        if user_id == LEO_USER_ID:
            return "assistant"

        return "user"
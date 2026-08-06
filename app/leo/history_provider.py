from app.infrastructure.ai.models import AIMessage
from app.infrastructure.conversation_store import ConversationStore


class HistoryProvider:
    """Преобразует историю диалога в сообщения AI."""

    def __init__(
        self,
        conversation_store: ConversationStore,
    ) -> None:
        self._conversation_store = conversation_store

    async def load(
        self,
        chat_id: int,
        limit: int = 20,
    ) -> list[AIMessage]:

        history = await self._conversation_store.get_last_messages(
            chat_id,
            limit,
        )

        messages: list[AIMessage] = []

        for message in history:

            role = "assistant"

            if message.user_id > 50:
                role = "user"

            messages.append(
                AIMessage(
                    role=role,
                    content=message.text or "",
                )
            )

        return messages
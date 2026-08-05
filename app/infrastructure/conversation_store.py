from app.context.conversation_context import ConversationContext
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.infrastructure.repositories.message_repository import MessageRepository
from app.infrastructure.repositories.user_repository import UserRepository


class ConversationStore:
    """Сохраняет данные разговора."""

    def __init__(
        self,
        user_repository: UserRepository,
        chat_repository: ChatRepository,
        message_repository: MessageRepository,
    ) -> None:
        self._user_repository = user_repository
        self._chat_repository = chat_repository
        self._message_repository = message_repository

    async def save(
        self,
        context: ConversationContext,
    ) -> None:
        await self._user_repository.upsert(
            context.user,
        )

        await self._chat_repository.upsert(
            context.chat,
        )

        await self._message_repository.insert(
            context.message,
        )
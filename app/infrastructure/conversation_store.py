from app.context.conversation_context import ConversationContext
from app.domain.message import Message
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.infrastructure.repositories.message_repository import MessageRepository
from app.infrastructure.repositories.user_repository import UserRepository


class ConversationStore:
    """Сохраняет и читает историю диалога."""

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

    async def save_outgoing_message(
        self,
        message: Message,
    ) -> None:
        await self._message_repository.insert(
            message,
        )

    async def get_last_messages(
        self,
        chat_id: int,
        limit: int = 20,
    ) -> list[Message]:
        return await self._message_repository.get_last_messages(
            chat_id,
            limit,
        )

    async def get_message(
        self,
        telegram_message_id: int,
    ) -> Message | None:
        return await self._message_repository.get_by_telegram_message_id(
            telegram_message_id,
        )
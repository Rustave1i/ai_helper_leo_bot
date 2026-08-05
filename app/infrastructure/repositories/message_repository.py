from app.domain.message import Message
from app.infrastructure.database.database import Database
from app.infrastructure.repositories.base import BaseRepository


class MessageRepository(BaseRepository):
    """Работа с таблицей Messages."""

    def __init__(
        self,
        database: Database,
    ) -> None:
        super().__init__(database)

    async def insert(
        self,
        message: Message,
    ) -> None:
        await self._database.execute(
            """
            INSERT INTO Messages
            (
                telegram_message_id,
                chat_id,
                user_id,
                reply_to_telegram_message_id,
                text,
                is_deleted
            )
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                message.telegram_message_id,
                message.chat_id,
                message.user_id,
                message.reply_to_telegram_message_id,
                message.text,
                message.is_deleted,
            ),
        )
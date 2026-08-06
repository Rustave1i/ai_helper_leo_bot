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

    async def get_last_messages(
        self,
        chat_id: int,
        limit: int = 20,
    ) -> list[Message]:

        rows = await self._database.fetch_all(
            """
            SELECT
                telegram_message_id,
                chat_id,
                user_id,
                reply_to_telegram_message_id,
                text,
                is_deleted
            FROM Messages
            WHERE chat_id = ?
            ORDER BY created_at DESC
            LIMIT ?;
            """,
            (
                chat_id,
                limit,
            ),
        )

        messages = [
            Message(
                telegram_message_id=row["telegram_message_id"],
                chat_id=row["chat_id"],
                user_id=row["user_id"],
                reply_to_telegram_message_id=row["reply_to_telegram_message_id"],
                text=row["text"],
                is_deleted=bool(row["is_deleted"]),
            )
            for row in rows
        ]

        messages.reverse()

        return messages
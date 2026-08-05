from app.domain.chat import Chat
from app.infrastructure.database.database import Database
from app.infrastructure.repositories.base import BaseRepository


class ChatRepository(BaseRepository):
    """Работа с таблицей Chats."""

    def __init__(
        self,
        database: Database,
    ) -> None:
        super().__init__(database)

    async def upsert(
        self,
        chat: Chat,
    ) -> None:
        await self._database.execute(
            """
            INSERT INTO Chats
            (
                telegram_chat_id,
                type,
                title,
                username
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(telegram_chat_id)
            DO UPDATE SET
                type = excluded.type,
                title = excluded.title,
                username = excluded.username,
                updated_at = CURRENT_TIMESTAMP;
            """,
            (
                chat.telegram_chat_id,
                chat.type,
                chat.title,
                chat.username,
            ),
        )
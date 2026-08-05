from app.domain.user import User
from app.infrastructure.database.database import Database
from app.infrastructure.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """Работа с таблицей Users."""

    def __init__(
        self,
        database: Database,
    ) -> None:
        super().__init__(database)

    async def upsert(
        self,
        user: User,
    ) -> None:
        await self._database.execute(
            """
            INSERT INTO Users
            (
                telegram_user_id,
                username,
                first_name,
                last_name,
                language_code,
                is_bot
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(telegram_user_id)
            DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                language_code = excluded.language_code,
                is_bot = excluded.is_bot,
                updated_at = CURRENT_TIMESTAMP;
            """,
            (
                user.telegram_user_id,
                user.username,
                user.first_name,
                user.last_name,
                user.language_code,
                user.is_bot,
            ),
        )
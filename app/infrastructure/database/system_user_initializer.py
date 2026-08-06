from app.domain.system_users import (
    LEO_USER_ID,
)
from app.domain.user import User
from app.infrastructure.repositories.user_repository import (
    UserRepository,
)


class SystemUserInitializer:
    """Создает системных пользователей."""

    def __init__(
        self,
        user_repository: UserRepository,
    ) -> None:
        self._user_repository = user_repository

    async def initialize(
        self,
    ) -> None:

        await self._user_repository.upsert(
            User(
                telegram_user_id=LEO_USER_ID,
                username="leo",
                first_name="Leo",
                last_name=None,
                language_code="ru",
                is_bot=True,
            )
        )
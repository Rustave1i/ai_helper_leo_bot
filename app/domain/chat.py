from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(slots=True)
class Chat:
    """Telegram-чат."""

    telegram_chat_id: int

    type: str

    title: str | None

    username: str | None

    created_at: datetime

    updated_at: datetime

    @classmethod
    def create(
        cls,
        telegram_chat_id: int,
        type: str,
        title: str | None,
        username: str | None,
    ) -> "Chat":
        """Создает новый чат."""

        now = datetime.now(
            UTC,
        )

        return cls(
            telegram_chat_id=telegram_chat_id,
            type=type,
            title=title,
            username=username,
            created_at=now,
            updated_at=now,
        )

    def touch(self) -> None:
        """Обновляет время изменения."""

        self.updated_at = datetime.now(
            UTC,
        )
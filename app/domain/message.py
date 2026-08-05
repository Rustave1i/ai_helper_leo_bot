from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(slots=True)
class Message:
    """Сообщение Telegram."""

    telegram_message_id: int

    chat_id: int

    user_id: int

    reply_to_telegram_message_id: int | None

    text: str | None

    created_at: datetime

    edited_at: datetime | None

    is_deleted: bool

    @classmethod
    def create(
        cls,
        telegram_message_id: int,
        chat_id: int,
        user_id: int,
        reply_to_telegram_message_id: int | None,
        text: str | None,
    ) -> "Message":
        """Создает новое сообщение."""

        return cls(
            telegram_message_id=telegram_message_id,
            chat_id=chat_id,
            user_id=user_id,
            reply_to_telegram_message_id=reply_to_telegram_message_id,
            text=text,
            created_at=datetime.now(
                UTC,
            ),
            edited_at=None,
            is_deleted=False,
        )

    def mark_deleted(self) -> None:
        """Помечает сообщение удаленным."""

        self.is_deleted = True

    def mark_edited(
        self,
        text: str | None,
    ) -> None:
        """Обновляет текст сообщения."""

        self.text = text

        self.edited_at = datetime.now(
            UTC,
        )
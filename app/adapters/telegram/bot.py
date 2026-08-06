from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.adapters.telegram.mapper import TelegramMapper
from app.config import settings
from app.domain.message import Message
from app.domain.system_users import LEO_USER_ID
from app.leo.assistant import Assistant


class TelegramBot:
    """Telegram-адаптер Leo."""

    def __init__(
        self,
        assistant: Assistant,
    ) -> None:
        self._assistant = assistant

        self._application = (
            Application.builder()
            .token(settings.telegram_token)
            .build()
        )

        self._application.add_handler(
            CommandHandler(
                "start",
                self.start,
            )
        )

        self._application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.message,
            )
        )

    async def start(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:

        if update.message is None:
            return

        await update.message.reply_text(
            "Привет! Я Leo 👋",
        )

    async def message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:

        if update.message is None:
            return

        conversation = TelegramMapper.map(
            update,
        )

        response = await self._assistant.handle(
            conversation,
        )

        if response is None:
            return

        reply = await update.message.reply_text(
            response.text,
        )

        await self._assistant._conversation_store.save_outgoing_message(
            Message(
                telegram_message_id=reply.message_id,
                chat_id=reply.chat.id,
                user_id=LEO_USER_ID,
                reply_to_telegram_message_id=update.message.message_id,
                text=response.text,
            )
        )

    def run(
        self,
    ) -> None:
        self._application.run_polling()
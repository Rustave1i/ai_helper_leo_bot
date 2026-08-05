from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

from app.adapters.telegram.mapper import TelegramMapper
from app.config import settings
from app.leo.assistant import Assistant


class TelegramBot:

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
                filters.ALL,
                self.message,
            )
        )

    async def start(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        await update.message.reply_text(
            "Привет! Я Leo 👋"
        )

    async def message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        conversation = TelegramMapper.map(
            update,
        )

        await self._assistant.handle(
            conversation,
        )

    def run(
        self,
    ) -> None:
        self._application.run_polling()
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config import BOT_TOKEN
from app.handlers.commands import (
    help_command,
    reset,
    start,
)
from app.handlers.messages import chat_message
from app.logger import logger


def main() -> None:
    """Точка входа Telegram-бота."""

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    application.add_handler(
        CommandHandler(
            "help",
            help_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "reset",
            reset,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat_message,
        )
    )

    logger.info("🤖 Бот запущен")

    application.run_polling()


if __name__ == "__main__":
    main()
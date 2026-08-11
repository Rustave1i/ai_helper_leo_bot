from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config import get_telegram_token
from app.core.container.container import container
from app.handlers.commands import (
    help_command,
    reset,
    start,
)
from app.handlers.messages import chat_message
from app.logger import logger


async def _post_shutdown(application: Application) -> None:
    await container.ai.close()


def main() -> None:
    """Точка входа Telegram-бота."""

    telegram_token = get_telegram_token()

    application = (
        Application.builder()
        .token(telegram_token)
        .post_shutdown(_post_shutdown)
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

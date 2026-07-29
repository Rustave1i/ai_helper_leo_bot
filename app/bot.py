from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config import BOT_TOKEN
from app.handlers.commands import (
    start,
    help_command,
    reset,
)
from app.handlers.messages import chat
from app.logger import logger

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset))

    # Обычные сообщения
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )

    logger.info("🤖 Бот запущен")

    application.run_polling()


if __name__ == "__main__":
    main()
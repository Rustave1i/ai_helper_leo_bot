from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config import (
    AI_PROVIDER,
    GIS_API_KEY,
    GEMINI_API_KEY,
    MISTRAL_API_KEY,
    OPENROUTER_API_KEY,
    TELEGRAM_TOKEN,
    YANDEX_API_KEY,
)
from app.database.engine import init_db
from app.handlers.commands import (
    start,
    help_command,
    reset,
)
from app.handlers.messages import chat, record_group_message
from app.logger import logger

# Фильтр только для групп: текстовые сообщения (не команды)
GROUP_FILTER = filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS


def _check_config() -> None:
    """Быстрая проверка критичных настроек до запуска poll."""
    if not TELEGRAM_TOKEN:
        raise SystemExit(
            "Ошибка: TELEGRAM_TOKEN не задан. Заполните .env "
            "(TELEGRAM_TOKEN из @BotFather)."
        )

    if AI_PROVIDER == "mistral" and not MISTRAL_API_KEY:
        raise SystemExit(
            "Ошибка: MISTRAL_API_KEY не задан (AI_PROVIDER=mistral)."
        )
    if AI_PROVIDER == "gemini" and not GEMINI_API_KEY:
        raise SystemExit(
            "Ошибка: GEMINI_API_KEY не задан (AI_PROVIDER=gemini)."
        )
    if AI_PROVIDER == "openrouter" and not OPENROUTER_API_KEY:
        raise SystemExit(
            "Ошибка: OPENROUTER_API_KEY не задан (AI_PROVIDER=openrouter)."
        )

    if not (GIS_API_KEY or YANDEX_API_KEY):
        logger.warning(
            "Не заданы ключи рейтингов (GIS_API_KEY / YANDEX_API_KEY). "
            "Инструмент совета будет работать без внешних рейтингов."
        )

    logger.warning(
        "ВАЖНО: в групповом чате включите у бота Privacy Mode OFF "
        "(@BotFather → /setprivacy → Disable), иначе бот не увидит "
        "обычные сообщения для контекста споров и саммари."
    )


def main():
    # Проверяем настройки до старта
    _check_config()

    # Создаём таблицы БД при старте
    init_db()

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset))

    # 1) Запись каждого группового сообщения в БД (всегда).
    #    Группа 0 — срабатывает первым у всех.
    application.add_handler(
        MessageHandler(GROUP_FILTER, record_group_message),
        group=0,
    )

    # 2) Обработка @упоминания / reply на бота.
    #    Группа 1 — срабатывает после записи.
    application.add_handler(
        MessageHandler(GROUP_FILTER, chat),
        group=1,
    )

    logger.info("🤖 Бот запущен")

    application.run_polling()


if __name__ == "__main__":
    main()

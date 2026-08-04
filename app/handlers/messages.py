import time

from telegram import Update
from telegram.ext import ContextTypes

from app.core.chat import chat
from app.logger import logger


async def chat_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Обработка текстовых сообщений."""

    if not update.message or not update.message.text:
        return

    user = update.effective_user

    if user is None:
        return

    user_text = update.message.text

    logger.info(
        'USER=%s | NAME="%s" | MESSAGE="%s"',
        user.id,
        user.full_name,
        user_text,
    )

    try:

        start = time.perf_counter()

        answer = chat.process(
            user_id=user.id,
            text=user_text,
        )

        elapsed = time.perf_counter() - start

        logger.info(
            "Ответ AI за %.2f сек.",
            elapsed,
        )

        await update.message.reply_text(answer)

    except Exception:

        logger.exception(
            "Ошибка ChatEngine"
        )

        await update.message.reply_text(
            "⚠️ Не удалось получить ответ от AI."
        )
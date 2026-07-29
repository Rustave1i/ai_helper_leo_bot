import time

from telegram import Update
from telegram.ext import ContextTypes

from app.services import chat_service
from app.logger import logger



async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычных текстовых сообщений."""

    if not update.message or not update.message.text:
        return

    user = update.effective_user
    user_text = update.message.text

    if user is None:
        return

    logger.info(
    'USER=%s | NAME="%s" | MESSAGE="%s"',
    user.id,
    user.full_name,
    user_text,
    )

    try:
        start = time.perf_counter()

        answer = chat_service.ask(
            user_id=user.id,
            message=user_text,
        )

        elapsed = time.perf_counter() - start

        logger.info(f"Mistral ответил за {elapsed:.2f} сек.")

        await update.message.reply_text(answer)

    except Exception:
        logger.exception("Ошибка при обращении к Mistral")

        await update.message.reply_text(
            "⚠️ Не удалось получить ответ от ИИ. Попробуйте позже."
        )
import time

from telegram import Update
from telegram.constants import ChatAction
from telegram.error import (
    NetworkError,
    TimedOut,
)
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

    text = update.message.text

    logger.info(
        'USER=%s | NAME="%s" | MESSAGE="%s"',
        user.id,
        user.full_name,
        text,
    )

    try:

        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING,
        )

        started = time.perf_counter()

        answer = await chat.process(
            user_id=user.id,
            text=text,
        )

        logger.info(
            "AI completed in %.2f sec",
            time.perf_counter() - started,
        )

        send_started = time.perf_counter()

        await update.message.reply_text(
            answer,
        )

        logger.info(
            "Telegram send in %.2f sec",
            time.perf_counter() - send_started,
        )

    except (TimedOut, NetworkError):

        logger.exception(
            "Telegram network error"
        )

    except Exception:

        logger.exception(
            "AI processing error"

        )

        try:

            await update.message.reply_text(
                "⚠️ Произошла ошибка при обработке запроса."
            )

        except Exception:

            logger.exception(
                "Не удалось отправить сообщение пользователю."
            )
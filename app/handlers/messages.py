import time

from telegram import Update
from telegram.error import (
    NetworkError,
    TimedOut,
)
from telegram.ext import ContextTypes

from app.core.chat import chat
from app.infrastructure.telegram import (
    TypingIndicator,
)
from app.logger import logger


async def chat_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not update.message or not update.message.text:
        return

    user = update.effective_user

    if user is None:
        return

    logger.info(
        'USER=%s | NAME="%s" | MESSAGE="%s"',
        user.id,
        user.full_name,
        update.message.text,
    )

    try:

        ai_started = time.perf_counter()

        async with TypingIndicator(
            context.bot,
            update.effective_chat.id,
        ):

            answer = chat.process(
                user_id=user.id,
                text=update.message.text,
            )

        logger.info(
            "AI completed in %.2f sec",
            time.perf_counter() - ai_started,
        )

        telegram_started = time.perf_counter()

        await update.message.reply_text(
            answer,
        )

        logger.info(
            "Telegram send in %.2f sec",
            time.perf_counter() - telegram_started,
        )

    except (TimedOut, NetworkError):

        logger.exception(
            "Telegram network error"
        )

    except Exception:

        logger.exception(
            "ChatEngine error"
        )
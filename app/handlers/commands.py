from telegram import Update
from telegram.ext import ContextTypes

from app.core.chat import chat


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if update.message:

        await update.message.reply_text(
            "Привет! Я AI Helper.\n\n"
            "Напиши любой вопрос."
        )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if update.message:

        await update.message.reply_text(
            "Доступные команды:\n\n"
            "/start\n"
            "/help\n"
            "/reset"
        )


async def reset(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    user = update.effective_user

    if user is None:
        return

    chat.reset(user.id)

    if update.message:

        await update.message.reply_text(
            "История очищена."
        )
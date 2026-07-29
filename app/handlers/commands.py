from telegram import Update
from telegram.ext import ContextTypes
from app.services import chat_service

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start."""

    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Я AI Helper Bot.\n"
        "Напишите мне любой вопрос."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help."""

    await update.message.reply_text(
        "Доступные команды:\n"
        "/start\n"
        "/help\n"
        "/reset\n"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистить историю диалога."""

    user = update.effective_user

    if user is None:
        return

    chat_service.reset(user.id)

    await update.message.reply_text(
        "🗑 История диалога очищена."
    )
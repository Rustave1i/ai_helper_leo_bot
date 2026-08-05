from telegram import Update

from app.context.conversation_context import ConversationContext
from app.domain.chat import Chat
from app.domain.message import Message
from app.domain.user import User


class TelegramMapper:
    """Преобразует Telegram Update в ConversationContext."""

    @staticmethod
    def map(update: Update) -> ConversationContext:
        message = update.effective_message
        chat = update.effective_chat
        user = update.effective_user

        return ConversationContext(
            chat=Chat(
                telegram_chat_id=chat.id,
                type=chat.type,
                title=chat.title,
                username=chat.username,
            ),
            user=User(
                telegram_user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code,
            ),
            message=Message(
                telegram_message_id=message.message_id,
                chat_id=chat.id,
                user_id=user.id,
                reply_to_telegram_message_id=(
                    message.reply_to_message.message_id
                    if message.reply_to_message
                    else None
                ),
                text=message.text,
            ),
        )
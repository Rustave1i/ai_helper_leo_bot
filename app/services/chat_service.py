from app.ai import ai
from app.tools import tool_manager


class ChatService:
    """Основной сервис общения с ИИ."""

    def ask(self, user_id: int, message: str) -> str:
        """
        Обрабатывает сообщение пользователя
        и возвращает ответ.
        """

        message = message.strip()

        if not message:
            return "Сообщение пустое."

        tool_answer = tool_manager.execute(message)

        if tool_answer is not None:
            return tool_answer

        return ai.ask(
            user_id=user_id,
            message=message,
        )

    def reset(self, user_id: int) -> None:
        """Очищает историю диалога пользователя."""

        ai.clear_history(user_id)
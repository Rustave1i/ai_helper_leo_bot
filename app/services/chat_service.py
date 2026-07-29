from app.ai import mistral
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

        # Сначала проверяем, может ли какой-либо инструмент
        # обработать запрос пользователя.
        tool_answer = tool_manager.execute(message)

        if tool_answer is not None:
            return tool_answer

        # Если ни один инструмент не подошел —
        # отправляем запрос в Mistral.
        return mistral.ask(
            user_id=user_id,
            message=message,
        )

    def reset(self, user_id: int) -> None:
        """Очищает историю диалога пользователя."""

        mistral.clear_history(user_id)
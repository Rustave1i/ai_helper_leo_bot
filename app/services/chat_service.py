from app.ai import ai
from app.models import conversation_store
from app.tools import tool_manager
from app.ai.prompts import SYSTEM_PROMPT


class ChatService:
    """Основной сервис общения с пользователем."""

    def __init__(self):
        self.ai = ai
        self.store = conversation_store
        self.tool_manager = tool_manager

    def ask(
        self,
        user_id: int,
        message: str,
    ) -> str:

        message = message.strip()

        if not message:
            return "Сообщение пустое."

        # Проверяем инструменты
        tool_answer = self.tool_manager.execute(message)

        if tool_answer is not None:
            return tool_answer

        # Сохраняем сообщение пользователя
        self.store.add(
            user_id,
            "user",
            message,
        )

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        messages.extend(
            self.store.get(user_id)
        )

        answer = self.ai.ask(messages)

        # Сохраняем ответ модели
        self.store.add(
            user_id,
            "assistant",
            answer,
        )

        return answer

    def reset(
        self,
        user_id: int,
    ) -> None:

        self.store.clear(user_id)
from app.core.ai.engine import AIEngine
from app.core.memory.chat_memory import ChatMemory
from app.core.models import Message, Role


class ConversationEngine:
    """Основной движок обработки диалогов."""

    def __init__(
        self,
        ai: AIEngine,
        memory: ChatMemory,
    ) -> None:

        self._ai = ai
        self._memory = memory

    def ask(
        self,
        user_id: int,
        text: str,
    ) -> str:
        """
        Обрабатывает сообщение пользователя
        и возвращает ответ AI.
        """

        text = text.strip()

        if not text:
            return "Сообщение пустое."

        user_message = Message(
            role=Role.USER,
            content=text,
        )

        self._memory.add(
            user_id=user_id,
            message=user_message,
        )

        history = list(
            self._memory.get(user_id)
        )

        answer = self._ai.ask(history)

        assistant_message = Message(
            role=Role.ASSISTANT,
            content=answer,
        )

        self._memory.add(
            user_id=user_id,
            message=assistant_message,
        )

        return answer

    def reset(
        self,
        user_id: int,
    ) -> None:
        """Очищает историю пользователя."""

        self._memory.clear(user_id)
from app.core.ai.engine import AIEngine
from app.core.memory.chat_memory import ChatMemory
from app.core.models import Message, Role


class ChatEngine:
    """Основной движок обработки диалогов."""

    def __init__(
        self,
        ai: AIEngine,
        memory: ChatMemory,
    ) -> None:

        self._ai = ai
        self._memory = memory

    def process(
        self,
        user_id: int,
        text: str,
    ) -> str:
        """Обрабатывает сообщение пользователя."""

        text = text.strip()

        if not text:
            return "Сообщение пустое."

        self._add_user_message(
            user_id=user_id,
            text=text,
        )

        answer = self._ai.ask(
            self._memory.get_history(user_id)
        )

        self._add_assistant_message(
            user_id=user_id,
            text=answer,
        )

        return answer

    def reset(
        self,
        user_id: int,
    ) -> None:
        """Очищает историю пользователя."""

        self._memory.clear(user_id)

    def _add_user_message(
        self,
        user_id: int,
        text: str,
    ) -> None:

        self._memory.add_message(
            user_id=user_id,
            message=Message(
                role=Role.USER,
                content=text,
            ),
        )

    def _add_assistant_message(
        self,
        user_id: int,
        text: str,
    ) -> None:

        self._memory.add_message(
            user_id=user_id,
            message=Message(
                role=Role.ASSISTANT,
                content=text,
            ),
        )
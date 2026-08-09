from app.core.ai.engine import AIEngine
from app.core.ai.prompts import SYSTEM_PROMPT
from app.core.memory.chat_memory import ChatMemory
from app.core.models import Message, Role
from app.core.tools import (
    ToolCall,
    ToolManager,
    ToolResult,
)


class ChatEngine:
    """Основной движок обработки диалогов."""

    def __init__(
        self,
        ai: AIEngine,
        memory: ChatMemory,
        tools: ToolManager,
    ) -> None:

        self._ai = ai
        self._memory = memory
        self._tools = tools

    async def process(
        self,
        user_id: int,
        text: str | ToolCall,
    ) -> str:

        if isinstance(text, ToolCall):

            tool_result = await self._tools.execute(
                text,
            )

            answer = self._tool_result_to_text(
                tool_result,
            )

            self._add_assistant_message(
                user_id=user_id,
                text=answer,
            )

            return answer

        text = text.strip()

        if not text:
            return "Сообщение пустое."

        self._add_user_message(
            user_id=user_id,
            text=text,
        )

        answer = await self._ai.ask(
            self._build_ai_context(
                user_id,
            )
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

        self._memory.clear(
            user_id,
        )

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

    def _build_ai_context(
        self,
        user_id: int,
    ) -> list[Message]:
        """Builds request context without persisting the system prompt."""

        return [
            Message(
                role=Role.SYSTEM,
                content=SYSTEM_PROMPT,
            ),
            *self._memory.get_history(
                user_id,
            ),
        ]

    @staticmethod
    def _tool_result_to_text(
        result: ToolResult,
    ) -> str:
        """Извлекает текст из результата инструмента для history и ответа."""

        return result.content

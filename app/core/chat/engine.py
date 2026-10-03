import asyncio

from app.core.ai.engine import AIEngine
from app.core.ai.prompts import SYSTEM_PROMPT
from app.core.memory.base_memory import BaseMemory
from app.core.models import ConversationKey, Message, Role
from app.core.tools import (
    ToolCall,
    ToolManager,
    ToolResult,
)


class ChatEngine:
    """Main conversation-processing engine."""

    def __init__(
        self,
        ai: AIEngine,
        memory: BaseMemory,
        tools: ToolManager,
    ) -> None:
        self._ai = ai
        self._memory = memory
        self._tools = tools
        self._locks: dict[ConversationKey, asyncio.Lock] = {}

    async def process(
        self,
        key: ConversationKey,
        text: str | ToolCall,
    ) -> str:
        async with self._lock_for(key):
            if isinstance(text, ToolCall):
                tool_result = await self._tools.execute(text)
                answer = self._tool_result_to_text(tool_result)
                self._add_assistant_message(key=key, text=answer)
                return answer

            text = text.strip()
            if not text:
                return "Сообщение пустое."

            self._add_user_message(key=key, text=text)
            answer = await self._ai.ask(self._build_ai_context(key))
            self._add_assistant_message(key=key, text=answer)
            return answer

    async def reset(self, key: ConversationKey) -> None:
        async with self._lock_for(key):
            self._memory.clear(key)

    def _add_user_message(
        self,
        key: ConversationKey,
        text: str,
    ) -> None:
        self._memory.append(
            key=key,
            message=Message(
                role=Role.USER,
                content=text,
            ),
        )

    def _add_assistant_message(
        self,
        key: ConversationKey,
        text: str,
    ) -> None:
        self._memory.append(
            key=key,
            message=Message(
                role=Role.ASSISTANT,
                content=text,
            ),
        )

    def _build_ai_context(
        self,
        key: ConversationKey,
    ) -> list[Message]:
        """Build request context without persisting the system prompt."""
        return [
            Message(
                role=Role.SYSTEM,
                content=SYSTEM_PROMPT,
            ),
            *self._memory.history(key),
        ]

    def _lock_for(self, key: ConversationKey) -> asyncio.Lock:
        """Return the persistent lock for one conversation key."""
        lock = self._locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[key] = lock
        return lock

    @staticmethod
    def _tool_result_to_text(
        result: ToolResult,
    ) -> str:
        """Extract text from a tool result for history and response."""
        return result.content
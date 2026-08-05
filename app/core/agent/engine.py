from app.core.ai.engine import AIEngine
from app.core.tools import ToolManager
from app.core.models import Message


class AgentEngine:
    """Главный координатор AI и инструментов."""

    def __init__(
        self,
        ai: AIEngine,
        tools: ToolManager,
    ) -> None:

        self._ai = ai
        self._tools = tools

    async def process(
        self,
        history: list[Message],
    ) -> str:
        """
        Пока просто вызывает AI.

        Позже здесь появится:
        - Tool Calling
        - RAG
        - Memory Search
        """

        return await self._ai.ask(
            history
        )
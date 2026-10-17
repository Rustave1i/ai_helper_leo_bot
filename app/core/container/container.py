from pathlib import Path

from app.config import MEMORY_DATABASE_PATH
from app.core.ai.engine import AIEngine
from app.core.chat.engine import ChatEngine
from app.core.memory.persistent_chat_memory import PersistentChatMemory
from app.core.memory.sqlite_conversation_repository import (
    SQLiteConversationRepository,
)
from app.core.tools import ToolManager
from app.core.tools.implementations import WeatherTool
from app.services.weather_service import WeatherService


class Container:
    """Контейнер зависимостей приложения."""

    def __init__(
        self,
        *,
        memory_database_path: str | Path | None = None,
    ) -> None:
        database_path = memory_database_path or MEMORY_DATABASE_PATH
        repository = SQLiteConversationRepository(database_path)
        self.memory = PersistentChatMemory(repository)

        self.ai = AIEngine()
        self.weather_service = WeatherService()
        self.tool_manager = self._build_tool_manager()

        self.chat = ChatEngine(
            ai=self.ai,
            memory=self.memory,
            tools=self.tool_manager,
        )

    def _build_tool_manager(self) -> ToolManager:
        """Создает и регистрирует инструменты."""
        manager = ToolManager()
        manager.register(WeatherTool(self.weather_service))
        return manager


container = Container()
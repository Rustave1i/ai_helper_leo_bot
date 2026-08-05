from app.core.ai.engine import AIEngine
from app.core.chat.engine import ChatEngine
from app.core.memory.chat_memory import ChatMemory
from app.core.tools import ToolManager
from app.core.tools.implementations import WeatherTool
from app.services.weather_service import WeatherService


class Container:
    """Контейнер зависимостей приложения."""

    def __init__(self) -> None:

        self.memory = ChatMemory()

        self.ai = AIEngine()

        self.weather_service = WeatherService()

        self.tool_manager = self._build_tool_manager()

        self.chat = ChatEngine(
            ai=self.ai,
            memory=self.memory,
            tools=self.tool_manager,
        )

    def _build_tool_manager(
        self,
    ) -> ToolManager:
        """Создает и регистрирует инструменты."""

        manager = ToolManager()

        manager.register(
            WeatherTool(
                self.weather_service,
            )
        )

        return manager


container = Container()
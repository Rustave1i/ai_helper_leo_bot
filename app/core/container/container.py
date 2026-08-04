from app.core.ai.engine import AIEngine
from app.core.chat.engine import ChatEngine
from app.core.memory.chat_memory import ChatMemory


class Container:
    """Контейнер зависимостей приложения."""

    def __init__(self) -> None:

        self.memory = ChatMemory()

        self.ai = AIEngine()

        self.chat = ChatEngine(
            ai=self.ai,
            memory=self.memory,
        )


container = Container()
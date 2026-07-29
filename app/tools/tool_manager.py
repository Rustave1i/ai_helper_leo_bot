from app.tools.registry import TOOLS


class ToolManager:
    """Управляет доступными инструментами."""

    def __init__(self):
        self.tools = [tool() for tool in TOOLS]

    def execute(self, message: str) -> str | None:
        """
        Возвращает ответ инструмента
        или None, если подходящего инструмента нет.
        """

        for tool in self.tools:
            if tool.can_handle(message):
                return tool.execute(message)

        return None
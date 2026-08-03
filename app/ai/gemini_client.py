from app.ai.base_client import BaseAIClient


class GeminiClient(BaseAIClient):
    """Временная реализация Gemini."""

    def ask(
        self,
        messages: list[dict],
    ) -> str:
        return "Gemini пока не подключен."
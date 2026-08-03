from app.ai.base_client import BaseAIClient


class GeminiClient(BaseAIClient):

    def ask(
        self,
        user_id: int,
        message: str,
    ) -> str:

        return "Gemini пока не подключен."

    def clear_history(
        self,
        user_id: int,
    ) -> None:
        pass
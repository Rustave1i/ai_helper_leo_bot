from app.config import settings
from app.infrastructure.ai.base import AIClient
from app.infrastructure.ai.openrouter import OpenRouterClient


def create_ai_client() -> AIClient:
    """Создает AI-клиент согласно настройкам."""

    match settings.ai_provider.lower():

        case "openrouter":
            return OpenRouterClient()

        case "mistral":
            raise NotImplementedError(
                "MistralClient еще не реализован."
            )

        case "gemini":
            raise NotImplementedError(
                "GeminiClient еще не реализован."
            )

        case _:
            raise ValueError(
                f"Неизвестный AI_PROVIDER: {settings.ai_provider}"
            )
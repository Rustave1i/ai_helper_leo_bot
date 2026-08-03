from app.config import AI_PROVIDER

from app.ai.gemini_client import GeminiClient
from app.ai.mistral_client import MistralClient


class ProviderFactory:

    _provider = None

    @classmethod
    def get_provider(cls):

        if cls._provider is not None:
            return cls._provider

        provider = AI_PROVIDER.lower()

        if provider == "gemini":
            cls._provider = GeminiClient()

        elif provider == "mistral":
            cls._provider = MistralClient()

        else:
            raise ValueError(
                f"Неизвестный AI_PROVIDER: {AI_PROVIDER}"
            )

        return cls._provider
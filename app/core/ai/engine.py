from app.config import AI_PROVIDER

from app.core.models import Message

from .gemini_client import GeminiClient
from .mistral_client import MistralClient
from .providers import AIProvider


class AIEngine:
    """Единая точка входа для работы с AI-провайдерами."""

    def __init__(self):

        self._clients = {
            AIProvider.GEMINI: GeminiClient(),
            AIProvider.MISTRAL: MistralClient(),
        }

        try:
            self._provider = AIProvider(
                AI_PROVIDER.lower()
            )

        except ValueError:
            self._provider = AIProvider.GEMINI

    @property
    def provider(self) -> AIProvider:
        """Текущий AI-провайдер."""
        return self._provider

    def set_provider(
        self,
        provider: AIProvider,
    ) -> None:
        """Переключает активного AI-провайдера."""

        self._provider = provider

    def ask(
        self,
        messages: list[Message],
    ) -> str:
        """
        Отправляет историю сообщений
        текущему AI-провайдеру.
        """

        client = self._clients[self._provider]

        return client.ask(messages)
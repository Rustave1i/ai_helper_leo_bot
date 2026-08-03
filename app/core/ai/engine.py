from app.config import AI_PROVIDER

from .providers import AIProvider
from .gemini_client import GeminiClient
from .mistral_client import MistralClient


class AIEngine:

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
        return self._provider

    def set_provider(
        self,
        provider: AIProvider,
    ):

        self._provider = provider

    def ask(
        self,
        messages: list[dict],
    ) -> str:

        client = self._clients[self._provider]

        return client.ask(messages)
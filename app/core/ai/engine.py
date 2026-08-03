from collections.abc import Sequence
from .providers.base_client import BaseAIClient
from app.logger import logger

from app.config import AI_PROVIDER
from app.core.models import Message

from .providers import (
    GeminiClient,
    MistralClient,
    OpenRouterClient,
)
from .provider_types import AIProvider


class AIEngine:
    """Единая точка входа для работы с AI-провайдерами."""

    def __init__(self) -> None:

        self._clients: dict[AIProvider, BaseAIClient] = {
            AIProvider.GEMINI: GeminiClient(),
            AIProvider.MISTRAL: MistralClient(),
            AIProvider.OPENROUTER: OpenRouterClient(),
        }

        try:
            self._provider = AIProvider(
                AI_PROVIDER.lower()
            )

        except ValueError:

            logger.warning(
                "Неизвестный AI_PROVIDER='%s'. Используется OpenRouter.",
                AI_PROVIDER,
            )

            self._provider = AIProvider.OPENROUTER

    @property
    def provider(self) -> AIProvider:
        return self._provider

    def set_provider(
        self,
        provider: AIProvider,
    ) -> None:

        self._provider = provider

    def ask(
        self,
        messages: Sequence[Message],
    ) -> str:

        client = self._clients[self._provider]

        logger.info(
            "AI Provider=%s Messages=%d",
            self._provider.value,
            len(messages),
        )

        return client.ask(messages)
from collections.abc import Sequence

from app.config import AI_PROVIDER
from app.core.models import Message
from app.logger import logger

from .provider_types import AIProvider
from .providers import (
    GeminiClient,
    MistralClient,
    OpenRouterClient,
)


class AIEngine:
    """Единая точка входа для AI-провайдеров."""

    def __init__(self) -> None:

        self._clients = {
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

    async def ask(
        self,
        messages: Sequence[Message],
    ) -> str:

        client = self._clients[
            self._provider
        ]

        logger.info(
            "AI Provider=%s Messages=%d",
            self._provider.value,
            len(messages),
        )

        return await client.ask(
            messages
        )
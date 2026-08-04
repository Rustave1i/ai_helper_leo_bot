from collections.abc import Sequence

from app.config import AI_PROVIDER
from app.core.ai.prompts import SYSTEM_PROMPT
from app.core.models import Message, Role
from app.logger import logger

from .provider_types import AIProvider
from .providers import (
    BaseAIClient,
    GeminiClient,
    MistralClient,
    OpenRouterClient,
)


class AIEngine:
    """Единая точка входа для работы с AI."""

    def __init__(self) -> None:

        self._provider = self._resolve_provider()

        self._client_classes: dict[
            AIProvider,
            type[BaseAIClient],
        ] = {
            AIProvider.GEMINI: GeminiClient,
            AIProvider.MISTRAL: MistralClient,
            AIProvider.OPENROUTER: OpenRouterClient,
        }

        self._client: BaseAIClient | None = None

    def _resolve_provider(self) -> AIProvider:

        try:
            return AIProvider(
                AI_PROVIDER.lower()
            )

        except ValueError:

            logger.warning(
                "Неизвестный AI_PROVIDER='%s'. Используется OpenRouter.",
                AI_PROVIDER,
            )

            return AIProvider.OPENROUTER

    def _get_client(self) -> BaseAIClient:

        if self._client is None:

            client_class = self._client_classes[
                self._provider
            ]

            self._client = client_class()

            logger.info(
                "Создан AI клиент: %s",
                client_class.__name__,
            )

        return self._client

    @property
    def provider(self) -> AIProvider:
        return self._provider

    def set_provider(
        self,
        provider: AIProvider,
    ) -> None:

        self._provider = provider
        self._client = None

    def ask(
        self,
        messages: Sequence[Message],
    ) -> str:

        payload = [
            Message(
                role=Role.SYSTEM,
                content=SYSTEM_PROMPT,
            )
        ]

        payload.extend(messages)

        logger.info(
            "AI Provider=%s Messages=%d",
            self._provider.value,
            len(payload),
        )

        return self._get_client().ask(payload)
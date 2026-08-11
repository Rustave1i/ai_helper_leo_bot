from collections.abc import Sequence

from app.config import (
    AI_PROVIDER,
    GEMINI_API_KEY,
    MISTRAL_API_KEY,
    OPENROUTER_API_KEY,
)
from app.core.models import Message
from app.logger import logger

from .provider_types import AIProvider
from .providers import GeminiClient, MistralClient, OpenRouterClient


class AIEngine:
    """Single entry point for AI providers."""

    def __init__(self) -> None:
        provider = self._resolve_provider(AI_PROVIDER)
        self._provider = provider
        self._client = self._create_client(provider)

    @staticmethod
    def _resolve_provider(value: str) -> AIProvider:
        try:
            return AIProvider(value.strip().lower())
        except (AttributeError, ValueError) as error:
            supported = ", ".join(provider.value for provider in AIProvider)
            raise ValueError(
                f"Unknown AI_PROVIDER. Supported values: {supported}."
            ) from error

    @staticmethod
    def _validate_credentials(provider: AIProvider) -> None:
        credentials = {
            AIProvider.GEMINI: (GEMINI_API_KEY, "GEMINI_API_KEY"),
            AIProvider.MISTRAL: (MISTRAL_API_KEY, "MISTRAL_API_KEY"),
            AIProvider.OPENROUTER: (
                OPENROUTER_API_KEY,
                "OPENROUTER_API_KEY",
            ),
        }
        api_key, setting = credentials[provider]
        if api_key is None or not api_key.strip():
            raise RuntimeError(
                f"AI provider '{provider.value}' is not configured. "
                f"Set {setting}."
            )

    def _create_client(self, provider: AIProvider):
        self._validate_credentials(provider)
        client_classes = {
            AIProvider.GEMINI: GeminiClient,
            AIProvider.MISTRAL: MistralClient,
            AIProvider.OPENROUTER: OpenRouterClient,
        }
        return client_classes[provider]()

    @property
    def provider(self) -> AIProvider:
        return self._provider

    def set_provider(self, provider: AIProvider) -> None:
        resolved_provider = self._resolve_provider(provider)
        client = self._create_client(resolved_provider)
        self._provider = resolved_provider
        self._client = client

    async def ask(self, messages: Sequence[Message]) -> str:
        logger.info(
            "AI Provider=%s Messages=%d",
            self._provider.value,
            len(messages),
        )
        return await self._client.ask(messages)

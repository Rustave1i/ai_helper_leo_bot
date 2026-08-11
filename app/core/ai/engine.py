import asyncio
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
        self._closed = False
        self._lifecycle_lock = asyncio.Lock()

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

    async def set_provider(self, provider: AIProvider) -> None:
        async with self._lifecycle_lock:
            self._ensure_open()
            resolved_provider = self._resolve_provider(provider)
            new_client = self._create_client(resolved_provider)
            old_provider = self._provider
            old_client = self._client
            self._provider = resolved_provider
            self._client = new_client

            if old_client is None:
                return

            try:
                await old_client.close()
            except Exception:
                logger.exception(
                    "Failed to close replaced AI provider=%s",
                    old_provider.value,
                )
                raise

    async def ask(self, messages: Sequence[Message]) -> str:
        async with self._lifecycle_lock:
            self._ensure_open()
            client = self._client
            if client is None:
                raise RuntimeError("AIEngine has no active client.")

            logger.info(
                "AI Provider=%s Messages=%d",
                self._provider.value,
                len(messages),
            )
            return await client.ask(messages)

    async def close(self) -> None:
        async with self._lifecycle_lock:
            if self._closed:
                return

            client = self._client
            self._client = None
            self._closed = True

            if client is not None:
                await client.close()

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("AIEngine is closed.")

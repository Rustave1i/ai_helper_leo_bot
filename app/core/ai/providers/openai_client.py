import asyncio
import time
from collections.abc import Sequence
from typing import Any

from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
)

from app.config import (
    HTTP_RETRIES,
    HTTP_RETRY_DELAY,
)
from app.core.infrastructure import (
    OpenAIFactory,
    RetryPolicy,
)
from app.core.models import Message
from app.logger import logger

from .base_ai_client import BaseAIClient


class OpenAIClient(BaseAIClient):
    """Базовый клиент для OpenAI-совместимых API."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        adapter: Any,
    ) -> None:

        self._adapter = adapter
        self._model = model

        self._client = OpenAIFactory.create(
            api_key=api_key,
            base_url=base_url,
        )

        self._retry = RetryPolicy(
            retries=HTTP_RETRIES,
            delay=HTTP_RETRY_DELAY,
        )

    async def ask(
        self,
        messages: Sequence[Message],
    ) -> str:

        payload = self._adapter.to_provider_format(
            messages
        )

        async def request():

            logger.info(
                "AI request"
            )

            started = time.perf_counter()

            response = await self._client.chat.completions.create(
                model=self._model,
                messages=payload,
            )

            elapsed = (
                time.perf_counter()
                - started
            )

            logger.info(
                "AI response %.2f sec",
                elapsed,
            )

            return self._adapter.from_provider_response(
                response
            )

        try:

            return await self._retry.execute(
                request,
                retry_on=(
                    APITimeoutError,
                    APIConnectionError,
                    InternalServerError,
                    RateLimitError,
                ),
            )

        except asyncio.CancelledError:

            logger.info(
                "AI request cancelled."
            )

            raise
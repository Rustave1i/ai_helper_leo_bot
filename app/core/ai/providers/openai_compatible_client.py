import time
from collections.abc import Sequence

from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)

from app.config import (
    HTTP_RETRIES,
    HTTP_RETRY_DELAY,
    HTTP_TIMEOUT,
)
from app.core.models import Message
from app.logger import logger

from .base_client import BaseAIClient


class OpenAICompatibleClient(BaseAIClient):
    """Базовый клиент для OpenAI-совместимых API."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        adapter,
    ) -> None:

        self._adapter = adapter
        self._model = model

        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=HTTP_TIMEOUT,
        )

    def ask(
        self,
        messages: Sequence[Message],
    ) -> str:

        payload = self._adapter.to_messages(
            messages
        )

        last_error = None

        for attempt in range(
            1,
            HTTP_RETRIES + 1,
        ):

            try:

                logger.info(
                    "AI request (%d/%d)",
                    attempt,
                    HTTP_RETRIES,
                )

                started = time.perf_counter()

                response = (
                    self._client.chat.completions.create(
                        model=self._model,
                        messages=payload,
                    )
                )

                elapsed = (
                    time.perf_counter()
                    - started
                )

                logger.info(
                    "AI response %.2f sec",
                    elapsed,
                )

                return (
                    response
                    .choices[0]
                    .message
                    .content
                    or ""
                )

            except (
                APITimeoutError,
                APIConnectionError,
                InternalServerError,
                RateLimitError,
            ) as ex:

                last_error = ex

                logger.warning(
                    "Попытка %d/%d завершилась ошибкой %s",
                    attempt,
                    HTTP_RETRIES,
                    type(ex).__name__,
                )

                if attempt < HTTP_RETRIES:

                    logger.info(
                        "Повтор через %d сек.",
                        HTTP_RETRY_DELAY,
                    )

                    time.sleep(
                        HTTP_RETRY_DELAY
                    )

        raise last_error
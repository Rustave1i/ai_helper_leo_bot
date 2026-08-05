import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from app.logger import logger

T = TypeVar("T")


class RetryPolicy:
    """Политика повторных попыток."""

    def __init__(
        self,
        retries: int,
        delay: int,
    ) -> None:

        self._retries = retries
        self._delay = delay

    async def execute(
        self,
        action: Callable[[], Awaitable[T]],
        *,
        retry_on: tuple[type[Exception], ...],
    ) -> T:

        last_error = None

        for attempt in range(
            1,
            self._retries + 1,
        ):

            try:

                return await action()

            except retry_on as ex:

                last_error = ex

                logger.warning(
                    "Попытка %d/%d завершилась ошибкой %s",
                    attempt,
                    self._retries,
                    type(ex).__name__,
                )

                if attempt < self._retries:

                    delay = (
                        self._delay * attempt
                    )

                    logger.info(
                        "Повтор через %d сек.",
                        delay,
                    )

                    await asyncio.sleep(
                        delay
                    )

        raise last_error
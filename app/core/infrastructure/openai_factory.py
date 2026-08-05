from httpx import Timeout
from openai import AsyncOpenAI

from app.config import HTTP_TIMEOUT


class OpenAIFactory:
    """Фабрика OpenAI-совместимых клиентов."""

    @staticmethod
    def create(
        *,
        api_key: str,
        base_url: str,
    ) -> AsyncOpenAI:

        timeout = Timeout(
            connect=10.0,
            read=float(HTTP_TIMEOUT),
            write=10.0,
            pool=10.0,
        )

        return AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )
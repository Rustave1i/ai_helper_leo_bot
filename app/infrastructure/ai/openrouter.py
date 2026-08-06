import httpx

from app.config import settings
from app.infrastructure.ai.base import AIClient
from app.infrastructure.ai.exceptions import (
    AIConnectionError,
    AIResponseError,
)
from app.infrastructure.ai.models import (
    AIRequest,
    AIResponse,
)


class OpenRouterClient(AIClient):
    """Клиент OpenRouter."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url="https://openrouter.ai/api/v1",
            timeout=settings.http_timeout,
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
        )

    async def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:

        payload = {
            "model": settings.openrouter_model,
            "messages": [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in request.messages
            ],
        }

        try:
            response = await self._client.post(
                "/chat/completions",
                json=payload,
            )

        except httpx.HTTPError as ex:
            raise AIConnectionError(
                "Не удалось подключиться к OpenRouter."
            ) from ex

        if response.status_code != 200:
            raise AIResponseError(
                f"OpenRouter вернул HTTP {response.status_code}: {response.text}"
            )

        data = response.json()

        return AIResponse(
            text=data["choices"][0]["message"]["content"],
        )

    async def close(self) -> None:
        await self._client.aclose()
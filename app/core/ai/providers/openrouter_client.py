from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)

from ..adapters.openrouter_adapter import OpenRouterAdapter

from .openai_client import OpenAIClient


class OpenRouterClient(OpenAIClient):
    """Клиент OpenRouter."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self) -> None:

        super().__init__(
            api_key=OPENROUTER_API_KEY,
            base_url=self.BASE_URL,
            model=OPENROUTER_MODEL,
            adapter=OpenRouterAdapter(),
        )
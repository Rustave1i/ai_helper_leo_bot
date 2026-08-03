from mistralai.client import Mistral

from app.ai.base_client import BaseAIClient
from app.config import (
    MISTRAL_API_KEY,
    MISTRAL_MODEL,
)


class MistralClient(BaseAIClient):
    """Клиент для работы с Mistral AI."""

    def __init__(self):
        self.client = Mistral(
            api_key=MISTRAL_API_KEY,
        )

    def ask(
        self,
        messages: list[dict],
    ) -> str:

        response = self.client.chat.complete(
            model=MISTRAL_MODEL,
            messages=messages,
        )

        return response.choices[0].message.content
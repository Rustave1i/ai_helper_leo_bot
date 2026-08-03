from mistralai.client import Mistral

from app.config import (
    MISTRAL_API_KEY,
    MISTRAL_MODEL,
)

from .base_client import BaseAIClient


class MistralClient(BaseAIClient):

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
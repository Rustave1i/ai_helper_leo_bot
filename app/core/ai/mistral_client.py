from collections.abc import Sequence

from mistralai.client import Mistral

from app.config import (
    MISTRAL_API_KEY,
    MISTRAL_MODEL,
)
from app.core.models import Message

from .adapters import MistralAdapter
from .base_client import BaseAIClient


class MistralClient(BaseAIClient):

    def __init__(self):

        self._client = Mistral(
            api_key=MISTRAL_API_KEY,
        )

        self._adapter = MistralAdapter()

    def ask(
        self,
        messages: Sequence[Message],
    ) -> str:

        payload = self._adapter.convert(messages)

        response = self._client.chat.complete(
            model=MISTRAL_MODEL,
            messages=payload,
        )

        answer = response.choices[0].message.content

        if answer is None:
            raise RuntimeError(
                "Mistral вернул пустой ответ."
            )

        return answer.strip()
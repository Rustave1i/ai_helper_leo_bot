from collections.abc import Sequence

from mistralai.client import Mistral

from app.config import (
    MISTRAL_API_KEY,
    MISTRAL_MODEL,
)
from app.core.models import Message

from ..adapters import MistralAdapter
from .base_ai_client import BaseAIClient


class MistralClient(BaseAIClient):
    """Клиент Mistral AI."""

    def __init__(self):

        self._client = Mistral(
            api_key=MISTRAL_API_KEY,
        )

        self._adapter = MistralAdapter()

    def ask(
        self,
        messages: Sequence[Message],
    ) -> str:

        payload = self._adapter.to_provider_format(
            messages
        )

        response = self._client.chat.complete(
            model=MISTRAL_MODEL,
            messages=payload,
        )

        return self._adapter.from_provider_response(
            response
        )
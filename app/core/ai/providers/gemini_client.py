from collections.abc import Sequence

from google import genai

from app.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
)
from app.core.models import Message

from ..adapters import GeminiAdapter
from .base_client import BaseAIClient


class GeminiClient(BaseAIClient):
    """Клиент Google Gemini."""

    def __init__(self):

        self._client = genai.Client(
            api_key=GEMINI_API_KEY,
        )

        self._adapter = GeminiAdapter()

    def ask(
        self,
        messages: Sequence[Message],
    ) -> str:

        contents = self._adapter.to_provider_format(
            messages
        )

        response = self._client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
        )

        return self._adapter.from_provider_response(
            response
        )
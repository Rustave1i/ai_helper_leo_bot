from collections.abc import Sequence

from openai import OpenAI

from app.core.models import Message

from ..adapters.base_adapter import BaseAdapter
from .base_client import BaseAIClient


class OpenAICompatibleClient(BaseAIClient):
    """
    Базовый клиент для OpenAI-совместимых API.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        adapter: BaseAdapter,
    ) -> None:

        self._model = model
        self._adapter = adapter

        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    def ask(
        self,
        messages: Sequence[Message],
    ) -> str:

        request = self._adapter.to_provider_format(
            messages
        )

        response = self._client.chat.completions.create(
            model=self._model,
            messages=request,
        )

        return self._adapter.from_provider_response(
            response
        )
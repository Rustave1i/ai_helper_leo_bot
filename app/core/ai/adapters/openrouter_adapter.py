from collections.abc import Sequence

from app.core.models import Message

from .base_adapter import BaseAdapter


class OpenRouterAdapter(BaseAdapter):

    def to_provider_format(
        self,
        messages: Sequence[Message],
    ) -> list[dict]:

        return [
            {
                "role": message.role.value,
                "content": message.content,
            }
            for message in messages
        ]

    def from_provider_response(
        self,
        response,
    ) -> str:

        answer = response.choices[0].message.content

        if answer is None:
            raise RuntimeError(
                "OpenRouter вернул пустой ответ."
            )

        return answer.strip()
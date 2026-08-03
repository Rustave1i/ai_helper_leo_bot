from collections.abc import Sequence

from app.core.models import Message

from .base_adapter import BaseAdapter


class MistralAdapter(BaseAdapter):

    def to_provider_format(
        self,
        messages: Sequence[Message],
    ) -> list[dict]:

        payload = []

        for message in messages:

            payload.append(
                {
                    "role": message.role.value,
                    "content": message.content,
                }
            )

        return payload

    def from_provider_response(
        self,
        response,
    ) -> str:

        answer = response.choices[0].message.content

        if answer is None:
            raise RuntimeError(
                "Mistral вернул пустой ответ."
            )

        return answer.strip()
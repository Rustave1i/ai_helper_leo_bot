from collections.abc import Sequence

from app.core.models import Message

from .base_adapter import BaseAdapter


class MistralAdapter(BaseAdapter):

    def convert(
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
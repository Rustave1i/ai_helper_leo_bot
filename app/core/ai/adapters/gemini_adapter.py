from collections.abc import Sequence

from app.core.models import Message, Role

from .base_adapter import BaseAdapter


class GeminiAdapter(BaseAdapter):

    def convert(
        self,
        messages: Sequence[Message],
    ) -> list[dict]:

        contents = []

        for message in messages:

            role = message.role.value

            if message.role == Role.ASSISTANT:
                role = "model"

            contents.append(
                {
                    "role": role,
                    "parts": [
                        {
                            "text": message.content,
                        }
                    ],
                }
            )

        return contents
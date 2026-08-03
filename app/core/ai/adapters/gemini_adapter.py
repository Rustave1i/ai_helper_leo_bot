from collections.abc import Sequence

from app.core.models import Message, Role

from .base_adapter import BaseAdapter


class GeminiAdapter(BaseAdapter):

    def to_provider_format(
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

    def from_provider_response(
        self,
        response,
    ) -> str:

        if response.text is None:
            raise RuntimeError(
                "Gemini вернул пустой ответ."
            )

        return response.text.strip()
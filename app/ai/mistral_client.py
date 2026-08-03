from mistralai.client import Mistral

from app.ai.base_client import BaseAIClient
from app.ai.prompts import SYSTEM_PROMPT
from app.config import MISTRAL_API_KEY, MODEL
from app.models.conversation import ConversationStore


class MistralClient(BaseAIClient):
    """Клиент для работы с Mistral AI."""

    def __init__(self):
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.store = ConversationStore()

    def ask(
        self,
        user_id: int,
        message: str,
    ) -> str:
        """Отправляет сообщение в Mistral с учетом истории."""

        self.store.add_message(
            user_id,
            "user",
            message,
        )

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        messages.extend(
            self.store.get_messages(user_id)
        )

        response = self.client.chat.complete(
            model=MODEL,
            messages=messages,
        )

        answer = response.choices[0].message.content

        self.store.add_message(
            user_id,
            "assistant",
            answer,
        )

        return answer

    def clear_history(
        self,
        user_id: int,
    ) -> None:
        self.store.clear(user_id)
from collections import defaultdict


class ConversationStore:
    """Хранит историю переписки пользователей."""

    MAX_MESSAGES = 20

    def __init__(self):
        self._conversations = defaultdict(list)

    def add_message(self, user_id: int, role: str, content: str):
        messages = self._conversations[user_id]

        messages.append(
            {
                "role": role,
                "content": content,
            }
        )

        # Оставляем только последние сообщения
        if len(messages) > self.MAX_MESSAGES:
            del messages[0]

    def get_messages(self, user_id: int):
        return self._conversations[user_id]

    def clear(self, user_id: int):
        self._conversations[user_id].clear()
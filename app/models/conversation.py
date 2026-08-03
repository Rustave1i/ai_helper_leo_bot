from collections import defaultdict


class ConversationStore:
    """Хранит историю переписки пользователей."""

    MAX_MESSAGES = 20

    def __init__(self):
        self._conversations = defaultdict(list)

    def add(
        self,
        user_id: int,
        role: str,
        content: str,
    ) -> None:

        messages = self._conversations[user_id]

        messages.append(
            {
                "role": role,
                "content": content,
            }
        )

        if len(messages) > self.MAX_MESSAGES:
            del messages[0]

    def get(
        self,
        user_id: int,
    ) -> list:

        return list(self._conversations[user_id])

    def clear(
        self,
        user_id: int,
    ) -> None:

        self._conversations[user_id].clear()

    def exists(
        self,
        user_id: int,
    ) -> bool:

        return user_id in self._conversations
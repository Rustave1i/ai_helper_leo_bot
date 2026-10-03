from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConversationKey:
    """Identifies one user's short-term context inside a chat."""

    chat_id: int
    user_id: int

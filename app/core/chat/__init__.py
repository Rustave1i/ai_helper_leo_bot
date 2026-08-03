from app.core.ai import ai
from app.core.memory import memory

from .engine import ConversationEngine


conversation = ConversationEngine(
    ai=ai,
    memory=memory,
)

__all__ = [
    "ConversationEngine",
    "conversation",
]
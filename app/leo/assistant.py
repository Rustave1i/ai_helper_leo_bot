from app.context.conversation_context import ConversationContext
from app.infrastructure.conversation_store import ConversationStore


class Assistant:
    """Главный координатор Leo."""

    def __init__(
        self,
        conversation_store: ConversationStore,
    ) -> None:
        self._conversation_store = conversation_store

    async def handle(
        self,
        context: ConversationContext,
    ) -> None:
        await self._conversation_store.save(context)

        if not self._is_addressed_to_leo(context):
            return

        # Здесь позже появится AI.

    def _is_addressed_to_leo(
        self,
        context: ConversationContext,
    ) -> bool:
        text = (context.message.text or "").lower()

        return (
            "@leo" in text
            or "лео" in text
            or "leo" in text
        )

async def handle(
    self,
    context: ConversationContext,
) -> None:

    print(
        f"[Assistant] {context.user.first_name}: {context.message.text}"
    )

    await self._conversation_store.save(
        context,
    )

    if not self._is_addressed_to_leo(
        context,
    ):
        return

    print("[Assistant] Leo mentioned")
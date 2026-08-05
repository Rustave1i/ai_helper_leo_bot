import asyncio

from telegram import Bot
from telegram.constants import ChatAction


class TypingIndicator:
    """Периодически показывает статус 'печатает...'."""

    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        interval: float = 4.0,
    ) -> None:

        self._bot = bot
        self._chat_id = chat_id
        self._interval = interval

        self._task: asyncio.Task | None = None

    async def __aenter__(self):

        self._task = asyncio.create_task(
            self._typing_loop()
        )

        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ):

        if self._task:

            self._task.cancel()

            try:
                await self._task

            except asyncio.CancelledError:
                pass

    async def _typing_loop(self):

        while True:

            await self._bot.send_chat_action(
                chat_id=self._chat_id,
                action=ChatAction.TYPING,
            )

            await asyncio.sleep(
                self._interval
            )
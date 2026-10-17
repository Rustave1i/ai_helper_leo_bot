import logging
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from telegram.constants import ChatAction
from telegram.error import NetworkError, TimedOut

from app.core.models import ConversationKey
from app.handlers import messages


class SafeLoggingHandlerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.text = "PRIVATE_TEXT_SENTINEL_7a3e\nsecond private line"
        self.name = "PRIVATE_NAME_SENTINEL_8b4f"
        self.user_id = 864209753186420
        self.answer = "OFFLINE_ANSWER_SENTINEL"
        self.message = SimpleNamespace(
            text=self.text,
            reply_text=AsyncMock(),
        )
        self.update = SimpleNamespace(
            message=self.message,
            effective_user=SimpleNamespace(id=self.user_id, full_name=self.name),
            effective_chat=SimpleNamespace(id=-123456),
        )
        self.context = SimpleNamespace(
            bot=SimpleNamespace(send_chat_action=AsyncMock()),
        )
        self.chat = SimpleNamespace(process=AsyncMock(return_value=self.answer))
        self.container_patch = patch.object(
            messages, "container", SimpleNamespace(chat=self.chat)
        )
        self.container_patch.start()
        self.addCleanup(self.container_patch.stop)

    async def _handle(self):
        with self.assertLogs(messages.logger, level="INFO") as captured:
            await messages.chat_message(self.update, self.context)
        # Format actual LogRecords, including exception text when present.
        formatter = logging.Formatter("%(levelname)s | %(message)s")
        rendered = "\n".join(formatter.format(record) for record in captured.records)
        for value in (self.text, self.text.splitlines()[0], self.name,
                      str(self.user_id), self.answer):
            self.assertNotIn(value, rendered)
        self.assertIn("Text message received", rendered)
        return captured.records, rendered

    async def test_success_logs_technical_events_without_user_data(self) -> None:
        records, rendered = await self._handle()

        self.chat.process.assert_awaited_once_with(
            key=ConversationKey(chat_id=-123456, user_id=self.user_id),
            text=self.text,
        )
        self.context.bot.send_chat_action.assert_awaited_once_with(
            chat_id=-123456, action=ChatAction.TYPING,
        )
        self.message.reply_text.assert_awaited_once_with(self.answer)
        self.assertRegex(rendered, r"AI completed in \d+\.\d{2} sec")
        self.assertRegex(rendered, r"Telegram send in \d+\.\d{2} sec")
        self.assertTrue(all(record.exc_info is None for record in records))

    async def test_typing_network_failure_keeps_error_diagnostic(self) -> None:
        self.context.bot.send_chat_action.side_effect = NetworkError(
            "offline typing transport failure"
        )

        records, rendered = await self._handle()

        self.chat.process.assert_not_awaited()
        self.message.reply_text.assert_not_awaited()
        self.assertIn("Telegram network error", rendered)
        self.assertIn("NetworkError", rendered)
        self.assertTrue(any(record.exc_info for record in records))

    async def test_reply_timeout_keeps_existing_response_behavior(self) -> None:
        self.message.reply_text.side_effect = TimedOut()

        _, rendered = await self._handle()

        self.message.reply_text.assert_awaited_once_with(self.answer)
        self.assertIn("AI completed in", rendered)
        self.assertIn("Telegram network error", rendered)
        self.assertIn("TimedOut", rendered)
        self.assertNotIn("Telegram send in", rendered)

    async def test_ai_failure_keeps_error_and_generic_reply(self) -> None:
        self.chat.process.side_effect = RuntimeError("offline provider failure")

        _, rendered = await self._handle()

        self.message.reply_text.assert_awaited_once_with(
            "⚠️ Произошла ошибка при обработке запроса."
        )
        self.assertIn("AI processing error", rendered)
        self.assertIn("RuntimeError: offline provider failure", rendered)

    async def test_error_reply_failure_keeps_both_diagnostics(self) -> None:
        self.chat.process.side_effect = RuntimeError("offline provider failure")
        self.message.reply_text.side_effect = RuntimeError("offline reply failure")

        records, rendered = await self._handle()

        self.message.reply_text.assert_awaited_once_with(
            "⚠️ Произошла ошибка при обработке запроса."
        )
        self.assertIn("AI processing error", rendered)
        self.assertIn("Не удалось отправить сообщение пользователю.", rendered)
        self.assertEqual(sum(record.levelno == logging.ERROR for record in records), 2)

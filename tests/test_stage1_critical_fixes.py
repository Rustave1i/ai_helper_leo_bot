import inspect
import unittest
from unittest.mock import patch

from app import config
from app.core.chat.engine import ChatEngine
from app.core.memory.chat_memory import ChatMemory
from app.core.models import Role
from app.core.tools import ToolCall, ToolResult


class FakeAI:
    def __init__(self) -> None:
        self.requests = []

    async def ask(self, messages):
        self.requests.append(list(messages))
        return "AI answer"


class FakeTools:
    def __init__(self) -> None:
        self.calls = []

    async def execute(self, call: ToolCall) -> ToolResult:
        self.calls.append(call)
        return ToolResult(success=True, content="Tool answer")


class TelegramTokenTests(unittest.TestCase):
    def test_missing_telegram_token_has_clear_error(self) -> None:
        with patch.object(config, "TELEGRAM_TOKEN", None):
            with self.assertRaisesRegex(
                RuntimeError,
                "TELEGRAM_TOKEN",
            ):
                config.get_telegram_token()

    def test_telegram_token_is_loaded(self) -> None:
        with patch.object(config, "TELEGRAM_TOKEN", "test-token"):
            self.assertEqual(
                config.get_telegram_token(),
                "test-token",
            )

    def test_bot_main_uses_validated_token_without_polling_network(self) -> None:
        from app import bot

        class FakeApplication:
            def __init__(self) -> None:
                self.handlers = []
                self.polling_started = False

            def add_handler(self, handler) -> None:
                self.handlers.append(handler)

            def run_polling(self) -> None:
                self.polling_started = True

        class FakeBuilder:
            def __init__(self) -> None:
                self.token_value = None
                self.post_shutdown_callback = None
                self.application = FakeApplication()

            def token(self, value):
                self.token_value = value
                return self

            def build(self):
                return self.application

            def post_shutdown(self, callback):
                self.post_shutdown_callback = callback
                return self

        builder = FakeBuilder()

        with (
            patch.object(bot.Application, "builder", return_value=builder),
            patch.object(bot, "get_telegram_token", return_value="test-token") as get_token,
            patch.object(bot.logger, "info"),
        ):
            bot.main()

        get_token.assert_called_once_with()
        self.assertEqual(builder.token_value, "test-token")
        self.assertTrue(
            inspect.iscoroutinefunction(builder.post_shutdown_callback)
        )
        self.assertTrue(builder.application.polling_started)
        self.assertEqual(len(builder.application.handlers), 4)


class ChatEngineStageOneTests(unittest.IsolatedAsyncioTestCase):
    async def test_plain_text_bypasses_tools_and_reaches_ai(self) -> None:
        ai = FakeAI()
        tools = FakeTools()
        memory = ChatMemory()
        engine = ChatEngine(ai=ai, memory=memory, tools=tools)

        answer = await engine.process(
            user_id=1,
            text="Hello",
        )

        self.assertEqual(answer, "AI answer")
        self.assertEqual(tools.calls, [])
        self.assertEqual(len(ai.requests), 1)
        self.assertEqual(
            ai.requests[0][1].content,
            "Hello",
        )
        self.assertEqual(
            ai.requests[0][1].role,
            Role.USER,
        )
        self.assertEqual(
            [message.content for message in memory.get_history(1)],
            ["Hello", "AI answer"],
        )

    async def test_tool_result_is_converted_to_text(self) -> None:
        ai = FakeAI()
        tools = FakeTools()
        memory = ChatMemory()
        engine = ChatEngine(ai=ai, memory=memory, tools=tools)

        answer = await engine.process(
            user_id=1,
            text=ToolCall(name="weather", arguments={}),
        )

        self.assertEqual(answer, "Tool answer")
        self.assertEqual(len(tools.calls), 1)
        self.assertEqual(ai.requests, [])
        history = memory.get_history(1)
        self.assertEqual(history[0].content, "Tool answer")
        self.assertIsInstance(history[0].content, str)

import subprocess
import sys
import unittest
from unittest.mock import patch


class CircularImportSmokeTests(unittest.TestCase):
    def test_container_and_chat_imports_share_the_container_engine(self) -> None:
        script = "\n".join(
            [
                "import importlib",
                "from unittest.mock import patch",
                "import app.core.ai.engine as ai_engine",
                "import app.core.chat.engine as chat_engine",
                "with patch.object(ai_engine, 'AIEngine', wraps=ai_engine.AIEngine) as ai_class:",
                "    with patch.object(chat_engine, 'ChatEngine', wraps=chat_engine.ChatEngine) as chat_class:",
                "        container_module = importlib.import_module('app.core.container.container')",
                "        importlib.import_module('app.core.chat')",
                "        container = container_module.container",
                "        assert ai_class.call_count == 1",
                "        assert chat_class.call_count == 1",
                "assert container.chat is not None",
                "assert container.chat._ai is container.ai",
                "print('composition import: OK')",
            ]
        )

        result = subprocess.run(
            [sys.executable, "-c", script],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("composition import: OK", result.stdout)

    def test_bot_main_reaches_application_creation_without_real_polling(self) -> None:
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
                self.application = FakeApplication()
                self.post_shutdown_callback = None

            def token(self, value):
                return self

            def post_shutdown(self, callback):
                self.post_shutdown_callback = callback
                return self

            def build(self):
                return self.application

        builder = FakeBuilder()

        with (
            patch.object(bot.Application, "builder", return_value=builder),
            patch.object(bot, "get_telegram_token", return_value="test-token"),
            patch.object(bot.logger, "info"),
        ):
            bot.main()

        self.assertTrue(builder.application.polling_started)
        self.assertEqual(len(builder.application.handlers), 4)
        self.assertIsNotNone(builder.post_shutdown_callback)

import importlib
import inspect
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import app.core.ai as ai_package
from app.core.ai import engine
from app.core.container.container import container


class CompositionShutdownTests(unittest.IsolatedAsyncioTestCase):
    def test_ai_package_exports_type_without_constructing_engine_or_provider(self):
        original_engine_class = engine.AIEngine

        with (
            patch.object(engine, "AIEngine", wraps=original_engine_class) as engine_class,
            patch.object(engine, "GeminiClient") as gemini_client,
            patch.object(engine, "MistralClient") as mistral_client,
            patch.object(engine, "OpenRouterClient") as openrouter_client,
        ):
            importlib.reload(ai_package)

            engine_class.assert_not_called()
            gemini_client.assert_not_called()
            mistral_client.assert_not_called()
            openrouter_client.assert_not_called()

        importlib.reload(ai_package)
        self.assertIs(ai_package.AIEngine, original_engine_class)
        self.assertFalse(hasattr(ai_package, "ai"))

    def test_container_chat_uses_container_ai(self):
        self.assertIs(container.chat._ai, container.ai)

    async def test_post_shutdown_closes_existing_container_engine_once(self):
        from app import bot

        close = AsyncMock()
        fake_container = SimpleNamespace(
            ai=SimpleNamespace(close=close),
        )

        with (
            patch.object(bot, "container", fake_container),
            patch.object(engine, "AIEngine") as engine_class,
        ):
            await bot._post_shutdown(None)

        close.assert_awaited_once_with()
        engine_class.assert_not_called()

    async def test_post_shutdown_callback_is_async(self):
        from app import bot

        self.assertTrue(inspect.iscoroutinefunction(bot._post_shutdown))

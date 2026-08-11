import unittest
from unittest.mock import patch

from app.core.ai import engine
from app.core.ai.provider_types import AIProvider
from app.core.models import Message, Role


class FakeClient:
    def __init__(self, answer: str = "AI answer") -> None:
        self.answer = answer
        self.requests = []

    async def ask(self, messages):
        self.requests.append(list(messages))
        return self.answer


class ProviderSelectionTests(unittest.IsolatedAsyncioTestCase):
    def _engine(self, provider: str, **credentials):
        values = {
            "AI_PROVIDER": provider,
            "GEMINI_API_KEY": "gemini-key",
            "MISTRAL_API_KEY": "mistral-key",
            "OPENROUTER_API_KEY": "openrouter-key",
        }
        values.update(credentials)
        return patch.multiple(engine, **values)

    async def test_openrouter_creates_only_openrouter_client_and_asks_it(self):
        openrouter = FakeClient("OpenRouter answer")
        with (
            self._engine("openrouter", GEMINI_API_KEY=None, MISTRAL_API_KEY=None),
            patch.object(engine, "OpenRouterClient", return_value=openrouter) as openrouter_class,
            patch.object(engine, "GeminiClient") as gemini_class,
            patch.object(engine, "MistralClient") as mistral_class,
        ):
            ai = engine.AIEngine()
            result = await ai.ask([Message(role=Role.USER, content="Hello")])

        self.assertEqual(ai.provider, AIProvider.OPENROUTER)
        self.assertEqual(result, "OpenRouter answer")
        openrouter_class.assert_called_once_with()
        gemini_class.assert_not_called()
        mistral_class.assert_not_called()
        self.assertEqual(openrouter.requests[0][0].content, "Hello")

    async def test_gemini_creates_only_gemini_client(self):
        with (
            self._engine("gemini", MISTRAL_API_KEY=None, OPENROUTER_API_KEY=None),
            patch.object(engine, "GeminiClient", return_value=FakeClient()) as gemini_class,
            patch.object(engine, "MistralClient") as mistral_class,
            patch.object(engine, "OpenRouterClient") as openrouter_class,
        ):
            ai = engine.AIEngine()

        self.assertEqual(ai.provider, AIProvider.GEMINI)
        gemini_class.assert_called_once_with()
        mistral_class.assert_not_called()
        openrouter_class.assert_not_called()

    async def test_mistral_creates_only_mistral_client(self):
        with (
            self._engine("mistral", GEMINI_API_KEY=None, OPENROUTER_API_KEY=None),
            patch.object(engine, "MistralClient", return_value=FakeClient()) as mistral_class,
            patch.object(engine, "GeminiClient") as gemini_class,
            patch.object(engine, "OpenRouterClient") as openrouter_class,
        ):
            ai = engine.AIEngine()

        self.assertEqual(ai.provider, AIProvider.MISTRAL)
        mistral_class.assert_called_once_with()
        gemini_class.assert_not_called()
        openrouter_class.assert_not_called()

    async def test_unknown_provider_fails_before_any_client_is_created(self):
        with (
            self._engine("unsupported"),
            patch.object(engine, "GeminiClient") as gemini_class,
            patch.object(engine, "MistralClient") as mistral_class,
            patch.object(engine, "OpenRouterClient") as openrouter_class,
            self.assertRaisesRegex(ValueError, "Unknown AI_PROVIDER"),
        ):
            engine.AIEngine()

        gemini_class.assert_not_called()
        mistral_class.assert_not_called()
        openrouter_class.assert_not_called()

    async def test_missing_selected_provider_credentials_fails_before_creation(self):
        with (
            self._engine("gemini", GEMINI_API_KEY=" "),
            patch.object(engine, "GeminiClient") as gemini_class,
            self.assertRaisesRegex(RuntimeError, "GEMINI_API_KEY"),
        ):
            engine.AIEngine()

        gemini_class.assert_not_called()

    async def test_set_provider_replaces_the_selected_client_lazily(self):
        gemini = FakeClient()
        mistral = FakeClient()
        with (
            self._engine("gemini"),
            patch.object(engine, "GeminiClient", return_value=gemini) as gemini_class,
            patch.object(engine, "MistralClient", return_value=mistral) as mistral_class,
            patch.object(engine, "OpenRouterClient") as openrouter_class,
        ):
            ai = engine.AIEngine()
            ai.set_provider(AIProvider.MISTRAL)

        self.assertEqual(ai.provider, AIProvider.MISTRAL)
        self.assertIs(ai._client, mistral)
        gemini_class.assert_called_once_with()
        mistral_class.assert_called_once_with()
        openrouter_class.assert_not_called()

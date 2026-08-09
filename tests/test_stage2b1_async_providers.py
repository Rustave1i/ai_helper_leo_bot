import inspect
import unittest

from app.config import GEMINI_MODEL, MISTRAL_MODEL
from app.core.ai.providers.gemini_client import GeminiClient
from app.core.ai.providers.mistral_client import MistralClient
from app.core.ai.providers.openai_client import OpenAIClient
from app.core.ai.providers.openrouter_client import OpenRouterClient
from app.core.models import Message, Role


class FakeAdapter:
    def __init__(self, payload, text):
        self.payload = payload
        self.text = text
        self.input_messages = None
        self.responses = []

    def to_provider_format(self, messages):
        self.input_messages = list(messages)
        return self.payload

    def from_provider_response(self, response):
        self.responses.append(response)
        return self.text


class FakeMistralChat:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    async def complete_async(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.response


class FakeMistralSDK:
    def __init__(self, chat):
        self.chat = chat


class FakeGeminiModels:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    async def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.response


class FakeGeminiAio:
    def __init__(self, models):
        self.models = models


class FakeGeminiSDK:
    def __init__(self, models):
        self.aio = FakeGeminiAio(models)


class AsyncProviderTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.messages = [Message(role=Role.USER, content="Hello")]

    async def test_mistral_ask_is_awaitable_and_uses_async_sdk(self):
        response = object()
        chat = FakeMistralChat(response=response)
        adapter = FakeAdapter(payload=[{"role": "user", "content": "Hello"}], text="Mistral answer")
        client = object.__new__(MistralClient)
        client._client = FakeMistralSDK(chat)
        client._adapter = adapter

        result = client.ask(self.messages)

        self.assertTrue(inspect.isawaitable(result))
        self.assertEqual(await result, "Mistral answer")
        self.assertEqual(
            chat.calls,
            [{"model": MISTRAL_MODEL, "messages": adapter.payload}],
        )
        self.assertEqual(adapter.input_messages, self.messages)
        self.assertEqual(adapter.responses, [response])

    async def test_mistral_sdk_error_propagates(self):
        chat = FakeMistralChat(error=RuntimeError("Mistral SDK failure"))
        client = object.__new__(MistralClient)
        client._client = FakeMistralSDK(chat)
        client._adapter = FakeAdapter(payload=[], text="unused")

        with self.assertRaisesRegex(RuntimeError, "Mistral SDK failure"):
            await client.ask(self.messages)

    async def test_gemini_ask_is_awaitable_and_uses_async_sdk(self):
        response = object()
        models = FakeGeminiModels(response=response)
        adapter = FakeAdapter(payload=["Hello"], text="Gemini answer")
        client = object.__new__(GeminiClient)
        client._client = FakeGeminiSDK(models)
        client._adapter = adapter

        result = client.ask(self.messages)

        self.assertTrue(inspect.isawaitable(result))
        self.assertEqual(await result, "Gemini answer")
        self.assertEqual(
            models.calls,
            [{"model": GEMINI_MODEL, "contents": adapter.payload}],
        )
        self.assertEqual(adapter.input_messages, self.messages)
        self.assertEqual(adapter.responses, [response])

    async def test_gemini_sdk_error_propagates(self):
        models = FakeGeminiModels(error=RuntimeError("Gemini SDK failure"))
        client = object.__new__(GeminiClient)
        client._client = FakeGeminiSDK(models)
        client._adapter = FakeAdapter(payload=[], text="unused")

        with self.assertRaisesRegex(RuntimeError, "Gemini SDK failure"):
            await client.ask(self.messages)

    def test_openrouter_uses_existing_async_openai_implementation(self):
        self.assertTrue(inspect.iscoroutinefunction(OpenRouterClient.ask))
        self.assertIs(OpenRouterClient.ask, OpenAIClient.ask)

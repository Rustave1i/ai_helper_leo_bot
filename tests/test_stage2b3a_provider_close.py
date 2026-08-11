import unittest

from app.core.ai.providers.gemini_client import GeminiClient
from app.core.ai.providers.mistral_client import MistralClient
from app.core.ai.providers.openai_client import OpenAIClient
from app.core.ai.providers.openrouter_client import OpenRouterClient
from app.core.models import Message, Role


class FakeGeminiAio:
    def __init__(self) -> None:
        self.close_calls = 0

    async def aclose(self) -> None:
        self.close_calls += 1


class FakeGeminiSDK:
    def __init__(self) -> None:
        self.aio = FakeGeminiAio()
        self.close_calls = 0

    def close(self) -> None:
        self.close_calls += 1


class FakeMistralSDK:
    def __init__(self) -> None:
        self.exit_calls = []
        self.async_client_close_calls = 0

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        self.exit_calls.append((exc_type, exc_value, traceback))
        self.async_client_close_calls += 1


class FakeOpenAISDK:
    def __init__(self) -> None:
        self.close_calls = 0

    async def close(self) -> None:
        self.close_calls += 1


class FakeAdapter:
    def to_provider_format(self, messages):
        return list(messages)

    def from_provider_response(self, response):
        return response


class FakeOpenAICompletions:
    async def create(self, **kwargs):
        return "answer"


class FakeOpenAIChat:
    def __init__(self) -> None:
        self.completions = FakeOpenAICompletions()


class FakeOpenAIRequestSDK(FakeOpenAISDK):
    def __init__(self) -> None:
        super().__init__()
        self.chat = FakeOpenAIChat()


class ProviderCloseTests(unittest.IsolatedAsyncioTestCase):
    async def test_gemini_close_closes_async_and_sync_clients_once(self) -> None:
        sdk = FakeGeminiSDK()
        client = object.__new__(GeminiClient)
        client._client = sdk
        client._closed = False

        await client.close()
        await client.close()

        self.assertEqual(sdk.aio.close_calls, 1)
        self.assertEqual(sdk.close_calls, 1)

    async def test_mistral_close_uses_async_context_exit_once(self) -> None:
        sdk = FakeMistralSDK()
        client = object.__new__(MistralClient)
        client._client = sdk
        client._closed = False

        await client.close()
        await client.close()

        self.assertEqual(sdk.exit_calls, [(None, None, None)])
        self.assertEqual(sdk.async_client_close_calls, 1)

    async def test_openai_close_closes_sdk_once(self) -> None:
        sdk = FakeOpenAISDK()
        client = object.__new__(OpenAIClient)
        client._client = sdk
        client._closed = False

        await client.close()
        await client.close()

        self.assertEqual(sdk.close_calls, 1)

    async def test_openrouter_inherits_openai_close_contract(self) -> None:
        sdk = FakeOpenAISDK()
        client = object.__new__(OpenRouterClient)
        client._client = sdk
        client._closed = False

        await client.close()
        await client.close()

        self.assertEqual(sdk.close_calls, 1)

    async def test_openai_ask_still_works_after_normal_initialization_state(self) -> None:
        client = object.__new__(OpenAIClient)
        client._client = FakeOpenAIRequestSDK()
        client._adapter = FakeAdapter()
        client._model = "test-model"
        client._closed = False

        class NoRetry:
            async def execute(self, request, retry_on):
                return await request()

        client._retry = NoRetry()

        result = await client.ask([Message(role=Role.USER, content="Hello")])

        self.assertEqual(result, "answer")

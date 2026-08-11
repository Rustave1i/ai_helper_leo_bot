import asyncio
import unittest
from unittest.mock import patch

from app.core.ai import engine
from app.core.ai.provider_types import AIProvider
from app.core.models import Message, Role


class FakeClient:
    def __init__(self, answer: str = "answer", close_error=None) -> None:
        self.answer = answer
        self.close_error = close_error
        self.close_calls = 0
        self.ask_calls = []

    async def ask(self, messages):
        self.ask_calls.append(list(messages))
        return self.answer

    async def close(self) -> None:
        self.close_calls += 1
        if self.close_error is not None:
            raise self.close_error


class BlockingClient(FakeClient):
    def __init__(self) -> None:
        super().__init__()
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def ask(self, messages):
        self.ask_calls.append(list(messages))
        self.started.set()
        await self.release.wait()
        return self.answer


class AIEngineLifecycleTests(unittest.IsolatedAsyncioTestCase):
    def _engine(self, client=None):
        ai = object.__new__(engine.AIEngine)
        ai._provider = AIProvider.GEMINI
        ai._client = client
        ai._closed = False
        ai._lifecycle_lock = asyncio.Lock()
        return ai

    async def test_close_closes_active_client_once_and_is_idempotent(self):
        client = FakeClient()
        ai = self._engine(client)

        await ai.close()
        await ai.close()

        self.assertEqual(client.close_calls, 1)
        self.assertTrue(ai._closed)
        self.assertIsNone(ai._client)

    async def test_close_without_client_is_safe(self):
        ai = self._engine()

        await ai.close()

        self.assertTrue(ai._closed)
        self.assertIsNone(ai._client)

    async def test_close_error_keeps_engine_closed_without_retrying_client(self):
        client = FakeClient(close_error=RuntimeError("close failed"))
        ai = self._engine(client)

        with self.assertRaisesRegex(RuntimeError, "close failed"):
            await ai.close()
        await ai.close()

        self.assertTrue(ai._closed)
        self.assertIsNone(ai._client)
        self.assertEqual(client.close_calls, 1)

    async def test_ask_and_set_provider_after_close_fail(self):
        ai = self._engine(FakeClient())
        await ai.close()

        with self.assertRaisesRegex(RuntimeError, "AIEngine is closed"):
            await ai.ask([Message(role=Role.USER, content="Hello")])
        with self.assertRaisesRegex(RuntimeError, "AIEngine is closed"):
            await ai.set_provider(AIProvider.MISTRAL)

    async def test_successful_set_provider_installs_new_client_then_closes_old(self):
        old_client = FakeClient()
        new_client = FakeClient()
        ai = self._engine(old_client)

        with patch.object(ai, "_create_client", return_value=new_client) as create_client:
            await ai.set_provider(AIProvider.MISTRAL)

        create_client.assert_called_once_with(AIProvider.MISTRAL)
        self.assertEqual(ai.provider, AIProvider.MISTRAL)
        self.assertIs(ai._client, new_client)
        self.assertEqual(old_client.close_calls, 1)

    async def test_new_provider_creation_error_preserves_old_client(self):
        old_client = FakeClient()
        ai = self._engine(old_client)

        with patch.object(ai, "_create_client", side_effect=RuntimeError("creation failed")):
            with self.assertRaisesRegex(RuntimeError, "creation failed"):
                await ai.set_provider(AIProvider.MISTRAL)

        self.assertEqual(ai.provider, AIProvider.GEMINI)
        self.assertIs(ai._client, old_client)
        self.assertEqual(old_client.close_calls, 0)

    async def test_old_client_close_error_keeps_new_client_active(self):
        old_client = FakeClient(close_error=RuntimeError("old close failed"))
        new_client = FakeClient()
        ai = self._engine(old_client)

        with patch.object(ai, "_create_client", return_value=new_client):
            with self.assertRaisesRegex(RuntimeError, "old close failed"):
                await ai.set_provider(AIProvider.MISTRAL)

        self.assertEqual(ai.provider, AIProvider.MISTRAL)
        self.assertIs(ai._client, new_client)
        self.assertEqual(old_client.close_calls, 1)

    async def test_ask_holds_lock_until_set_provider_can_close_old_client(self):
        old_client = BlockingClient()
        new_client = FakeClient()
        ai = self._engine(old_client)

        ask_task = asyncio.create_task(
            ai.ask([Message(role=Role.USER, content="Hello")])
        )
        await old_client.started.wait()

        with patch.object(ai, "_create_client", return_value=new_client):
            switch_task = asyncio.create_task(ai.set_provider(AIProvider.MISTRAL))
            await asyncio.sleep(0)
            self.assertEqual(old_client.close_calls, 0)
            self.assertFalse(switch_task.done())
            old_client.release.set()
            await ask_task
            await switch_task

        self.assertEqual(old_client.close_calls, 1)
        self.assertIs(ai._client, new_client)

    async def test_ask_holds_lock_until_close_can_close_client(self):
        client = BlockingClient()
        ai = self._engine(client)

        ask_task = asyncio.create_task(
            ai.ask([Message(role=Role.USER, content="Hello")])
        )
        await client.started.wait()
        close_task = asyncio.create_task(ai.close())
        await asyncio.sleep(0)
        self.assertEqual(client.close_calls, 0)
        self.assertFalse(close_task.done())
        client.release.set()
        await ask_task
        await close_task

        self.assertEqual(client.close_calls, 1)
        self.assertTrue(ai._closed)

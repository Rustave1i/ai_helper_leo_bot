import asyncio
import unittest
from collections import defaultdict
from typing import Sequence

from app.core.ai.prompts import SYSTEM_PROMPT
from app.core.chat.engine import ChatEngine
from app.core.memory.base_memory import BaseMemory
from app.core.memory.chat_memory import ChatMemory
from app.core.models import ConversationKey, Message, Role


class BlockingAI:
    def __init__(self, *texts: str) -> None:
        self.started = {text: asyncio.Event() for text in texts}
        self.release = {text: asyncio.Event() for text in texts}
        self.requests: list[list[Message]] = []

    async def ask(self, messages: Sequence[Message]) -> str:
        request = list(messages)
        self.requests.append(request)
        text = request[-1].content
        self.started[text].set()
        await self.release[text].wait()
        return f"answer:{text}"


class UnusedTools:
    async def execute(self, call):
        raise AssertionError("Tools are not used in these tests")


class KeyedOnlyMemory(BaseMemory):
    def __init__(self) -> None:
        self._histories: dict[ConversationKey, list[Message]] = defaultdict(list)

    def append(self, key: ConversationKey, message: Message) -> None:
        self._histories[key].append(message)

    def history(
        self,
        key: ConversationKey,
        limit: int | None = None,
    ) -> Sequence[Message]:
        messages = self._histories[key]
        return list(messages if limit is None else messages[-limit:])

    def clear(self, key: ConversationKey) -> None:
        self._histories[key].clear()


class ChatEngineKeyedConcurrencyTests(unittest.IsolatedAsyncioTestCase):
    async def test_same_key_requests_are_serialized(self) -> None:
        key = ConversationKey(chat_id=10, user_id=1)
        ai = BlockingAI("first", "second")
        memory = ChatMemory()
        engine = ChatEngine(ai=ai, memory=memory, tools=UnusedTools())

        first = asyncio.create_task(engine.process(key=key, text="first"))
        await ai.started["first"].wait()

        second = asyncio.create_task(engine.process(key=key, text="second"))
        await asyncio.sleep(0)
        self.assertFalse(ai.started["second"].is_set())

        ai.release["first"].set()
        await ai.started["second"].wait()
        ai.release["second"].set()

        self.assertEqual(
            await asyncio.gather(first, second),
            ["answer:first", "answer:second"],
        )
        self.assertEqual(
            [message.content for message in memory.history(key)],
            ["first", "answer:first", "second", "answer:second"],
        )

    async def test_different_keys_progress_independently_and_are_isolated(self) -> None:
        first_key = ConversationKey(chat_id=10, user_id=1)
        second_key = ConversationKey(chat_id=20, user_id=1)
        ai = BlockingAI("first", "second")
        memory = ChatMemory()
        engine = ChatEngine(ai=ai, memory=memory, tools=UnusedTools())

        first = asyncio.create_task(engine.process(key=first_key, text="first"))
        second = asyncio.create_task(engine.process(key=second_key, text="second"))

        await asyncio.wait_for(
            asyncio.gather(
                ai.started["first"].wait(),
                ai.started["second"].wait(),
            ),
            timeout=0.2,
        )
        ai.release["first"].set()
        ai.release["second"].set()
        await asyncio.gather(first, second)

        self.assertEqual(
            [message.content for message in memory.history(first_key)],
            ["first", "answer:first"],
        )
        self.assertEqual(
            [message.content for message in memory.history(second_key)],
            ["second", "answer:second"],
        )

    async def test_reset_waits_for_active_process_on_the_same_key(self) -> None:
        key = ConversationKey(chat_id=10, user_id=1)
        ai = BlockingAI("first")
        memory = ChatMemory()
        engine = ChatEngine(ai=ai, memory=memory, tools=UnusedTools())

        process = asyncio.create_task(engine.process(key=key, text="first"))
        await ai.started["first"].wait()

        reset = asyncio.create_task(engine.reset(key))
        await asyncio.sleep(0)
        self.assertFalse(reset.done())

        ai.release["first"].set()
        await asyncio.gather(process, reset)

        self.assertEqual(memory.history(key), [])

    async def test_chat_engine_uses_only_keyed_memory_contract(self) -> None:
        key = ConversationKey(chat_id=10, user_id=1)
        memory = KeyedOnlyMemory()

        class ImmediateAI:
            async def ask(self, messages: Sequence[Message]) -> str:
                return "answer"

        engine = ChatEngine(
            ai=ImmediateAI(),
            memory=memory,
            tools=UnusedTools(),
        )

        await engine.process(key=key, text="hello")

        self.assertFalse(hasattr(memory, "add_message"))
        self.assertFalse(hasattr(memory, "get_history"))
        self.assertEqual(
            [message.content for message in memory.history(key)],
            ["hello", "answer"],
        )
        self.assertNotIn(
            Role.SYSTEM,
            [message.role for message in memory.history(key)],
        )

    async def test_system_prompt_is_only_in_the_provider_request(self) -> None:
        key = ConversationKey(chat_id=10, user_id=1)
        ai = BlockingAI("hello")
        memory = ChatMemory()
        engine = ChatEngine(ai=ai, memory=memory, tools=UnusedTools())

        request = asyncio.create_task(engine.process(key=key, text="hello"))
        await ai.started["hello"].wait()
        self.assertEqual(ai.requests[0][0].content, SYSTEM_PROMPT)
        ai.release["hello"].set()
        await request

        self.assertNotIn(
            Role.SYSTEM,
            [message.role for message in memory.history(key)],
        )
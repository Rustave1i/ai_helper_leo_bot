import unittest

from app.core.ai.prompts import SYSTEM_PROMPT
from app.core.chat.engine import ChatEngine
from app.core.memory.chat_memory import ChatMemory
from app.core.models import ConversationKey, Message, Role


class FakeAI:
    def __init__(self) -> None:
        self.requests = []

    async def ask(self, messages):
        self.requests.append(list(messages))
        return "AI answer"


class UnusedTools:
    async def execute(self, call):
        raise AssertionError("Plain text must not execute tools")


class SystemPromptContextTests(unittest.IsolatedAsyncioTestCase):
    def _engine(self, memory: ChatMemory | None = None):
        ai = FakeAI()
        engine = ChatEngine(
            ai=ai,
            memory=memory or ChatMemory(),
            tools=UnusedTools(),
        )
        return engine, ai

    def _key(self) -> ConversationKey:
        return ConversationKey(chat_id=100, user_id=1)

    async def test_system_prompt_is_first_before_existing_history(self) -> None:
        key = self._key()
        memory = ChatMemory()
        memory.append(
            key,
            Message(role=Role.USER, content="Previous user message"),
        )
        memory.append(
            key,
            Message(role=Role.ASSISTANT, content="Previous assistant message"),
        )
        engine, ai = self._engine(memory)

        await engine.process(key=key, text="Current user message")

        request = ai.requests[0]
        self.assertEqual(request[0].role, Role.SYSTEM)
        self.assertEqual(request[0].content, SYSTEM_PROMPT)
        self.assertEqual(
            [message.content for message in request[1:]],
            [
                "Previous user message",
                "Previous assistant message",
                "Current user message",
            ],
        )

    async def test_system_prompt_is_not_saved_in_memory(self) -> None:
        key = self._key()
        memory = ChatMemory()
        engine, _ = self._engine(memory)

        await engine.process(key=key, text="Hello")

        self.assertNotIn(
            Role.SYSTEM,
            [message.role for message in memory.history(key)],
        )

    async def test_system_prompt_does_not_duplicate_between_requests(self) -> None:
        key = self._key()
        memory = ChatMemory()
        engine, ai = self._engine(memory)

        await engine.process(key=key, text="First")
        await engine.process(key=key, text="Second")

        second_request = ai.requests[1]
        self.assertEqual(
            sum(message.role == Role.SYSTEM for message in second_request),
            1,
        )
        self.assertNotIn(
            Role.SYSTEM,
            [message.role for message in memory.history(key)],
        )

    async def test_first_message_request_contains_system_then_user(self) -> None:
        key = self._key()
        engine, ai = self._engine()

        await engine.process(key=key, text="Hello")

        request = ai.requests[0]
        self.assertEqual(
            [(message.role, message.content) for message in request],
            [
                (Role.SYSTEM, SYSTEM_PROMPT),
                (Role.USER, "Hello"),
            ],
        )
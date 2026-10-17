import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core.chat.engine import ChatEngine
from app.core.container.container import Container
from app.core.memory.persistent_chat_memory import PersistentChatMemory
from app.core.memory.sqlite_conversation_repository import (
    SQLiteConversationRepository,
)
from app.core.models import ConversationKey, Message, Role


class RecordingAI:
    def __init__(self) -> None:
        self.requests: list[list[Message]] = []

    async def ask(self, messages: list[Message]) -> str:
        request = list(messages)
        self.requests.append(request)
        return f"answer:{request[-1].content}"


class UnusedTools:
    async def execute(self, call):
        raise AssertionError("Tools are not used in persistent-memory tests")


class InertAI:
    async def ask(self, messages):
        return "unused"

    async def close(self) -> None:
        return None


class PersistentChatMemoryTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self._temporary_directory.name) / "memory.sqlite3"
        self.key = ConversationKey(chat_id=100, user_id=1)
        self.other_key = ConversationKey(chat_id=200, user_id=1)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def _memory(self) -> PersistentChatMemory:
        return PersistentChatMemory(
            SQLiteConversationRepository(self.database_path)
        )

    def test_append_history_clear_and_key_isolation(self) -> None:
        memory = self._memory()
        memory.append(
            self.key,
            Message(role=Role.USER, content="first"),
        )
        memory.append(
            self.other_key,
            Message(role=Role.ASSISTANT, content="other"),
        )

        self.assertEqual(
            [message.content for message in memory.history(self.key)],
            ["first"],
        )
        memory.clear(self.key)
        self.assertEqual(memory.history(self.key), [])
        self.assertEqual(
            [message.content for message in memory.history(self.other_key)],
            ["other"],
        )

    def test_history_is_bounded_and_persists_after_restart(self) -> None:
        memory = self._memory()
        for number in range(25):
            memory.append(
                self.key,
                Message(role=Role.USER, content=str(number)),
            )

        restored = self._memory()

        self.assertEqual(
            [message.content for message in restored.history(self.key)],
            [str(number) for number in range(5, 25)],
        )

    def test_system_message_is_not_persisted(self) -> None:
        memory = self._memory()

        with self.assertRaisesRegex(ValueError, "System messages"):
            memory.append(
                self.key,
                Message(role=Role.SYSTEM, content="system"),
            )

        self.assertEqual(memory.history(self.key), [])

    async def test_chat_engine_uses_persistent_history_for_telegram_like_flow(self) -> None:
        memory = self._memory()
        ai = RecordingAI()
        chat = ChatEngine(ai=ai, memory=memory, tools=UnusedTools())

        await chat.process(key=self.key, text="first")
        await chat.process(key=self.key, text="second")

        self.assertEqual(
            [message.content for message in ai.requests[1][1:]],
            ["first", "answer:first", "second"],
        )

        restored = self._memory()
        self.assertEqual(
            [message.content for message in restored.history(self.key)],
            ["first", "answer:first", "second", "answer:second"],
        )

    def test_new_container_restores_history_from_the_same_database(self) -> None:
        with patch("app.core.container.container.AIEngine", InertAI):
            first = Container(memory_database_path=self.database_path)
            first.memory.append(
                self.key,
                Message(role=Role.USER, content="Hello"),
            )
            first.memory.append(
                self.key,
                Message(role=Role.ASSISTANT, content="Hi"),
            )
            del first

            restored = Container(memory_database_path=self.database_path)

        self.assertEqual(
            restored.memory.history(self.key),
            [
                Message(role=Role.USER, content="Hello"),
                Message(role=Role.ASSISTANT, content="Hi"),
            ],
        )
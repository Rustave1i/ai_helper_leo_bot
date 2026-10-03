import unittest

from app.core.ai.prompts import SYSTEM_PROMPT
from app.core.chat.engine import ChatEngine
from app.core.memory.chat_memory import ChatMemory
from app.core.models import ConversationKey, Message, Role


class FakeAI:
    async def ask(self, messages):
        return "AI answer"


class UnusedTools:
    async def execute(self, call):
        raise AssertionError("Tools are not used in this test")


class ConversationKeyTests(unittest.TestCase):
    def test_equality_and_hashability(self):
        first = ConversationKey(chat_id=100, user_id=1)
        same = ConversationKey(chat_id=100, user_id=1)

        self.assertEqual(first, same)
        self.assertEqual({first: "history"}[same], "history")

    def test_different_chat_or_user_creates_different_key(self):
        key = ConversationKey(chat_id=100, user_id=1)

        self.assertNotEqual(key, ConversationKey(chat_id=200, user_id=1))
        self.assertNotEqual(key, ConversationKey(chat_id=100, user_id=2))


class ChatMemoryIdentityTests(unittest.TestCase):
    def setUp(self):
        self.memory = ChatMemory()
        self.first = ConversationKey(chat_id=100, user_id=1)
        self.second = ConversationKey(chat_id=200, user_id=1)

    def test_history_isolated_by_conversation_key(self):
        self.memory.append(
            self.first,
            Message(role=Role.USER, content="First chat"),
        )
        self.memory.append(
            self.second,
            Message(role=Role.USER, content="Second chat"),
        )

        self.assertEqual(
            [message.content for message in self.memory.history(self.first)],
            ["First chat"],
        )
        self.assertEqual(
            [message.content for message in self.memory.history(self.second)],
            ["Second chat"],
        )

    def test_history_isolated_by_user_in_same_chat(self):
        other_user = ConversationKey(chat_id=100, user_id=2)
        self.memory.append(
            self.first,
            Message(role=Role.USER, content="First user"),
        )
        self.memory.append(
            other_user,
            Message(role=Role.USER, content="Second user"),
        )

        self.assertEqual(
            [message.content for message in self.memory.history(self.first)],
            ["First user"],
        )
        self.assertEqual(
            [message.content for message in self.memory.history(other_user)],
            ["Second user"],
        )

    def test_clear_affects_only_selected_key(self):
        for key in (self.first, self.second):
            self.memory.append(
                key,
                Message(role=Role.USER, content=str(key.chat_id)),
            )

        self.memory.clear(self.first)

        self.assertEqual(self.memory.history(self.first), [])
        self.assertEqual(
            [message.content for message in self.memory.history(self.second)],
            ["200"],
        )

    def test_max_messages_and_oldest_to_newest_order(self):
        for number in range(25):
            self.memory.append(
                self.first,
                Message(role=Role.USER, content=str(number)),
            )

        history = self.memory.history(self.first)

        self.assertEqual(len(history), ChatMemory.MAX_MESSAGES)
        self.assertEqual(
            [message.content for message in history],
            [str(n) for n in range(5, 25)],
        )

    def test_history_limit_returns_newest_messages_in_order(self):
        for number in range(4):
            self.memory.append(
                self.first,
                Message(role=Role.USER, content=str(number)),
            )

        self.assertEqual(
            [message.content for message in self.memory.history(self.first, limit=2)],
            ["2", "3"],
        )

    def test_history_limit_zero_returns_empty(self):
        self.memory.append(
            self.first,
            Message(role=Role.USER, content="Message"),
        )

        self.assertEqual(self.memory.history(self.first, limit=0), [])

    def test_system_message_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "System messages"):
            self.memory.append(
                self.first,
                Message(role=Role.SYSTEM, content=SYSTEM_PROMPT),
            )

        self.assertEqual(self.memory.history(self.first), [])


class SystemPromptFlowTests(unittest.IsolatedAsyncioTestCase):
    async def test_chat_engine_does_not_store_system_prompt(self):
        key = ConversationKey(chat_id=100, user_id=1)
        memory = ChatMemory()
        chat = ChatEngine(ai=FakeAI(), memory=memory, tools=UnusedTools())

        await chat.process(key=key, text="Hello")

        self.assertNotIn(
            Role.SYSTEM,
            [message.role for message in memory.history(key)],
        )
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from app.core.memory.sqlite_conversation_repository import (
    SQLiteConversationRepository,
)
from app.core.models import ConversationKey, Message, Role


class SQLiteConversationRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self._temporary_directory.name) / "memory.sqlite3"
        self.key = ConversationKey(chat_id=100, user_id=1)
        self.other_key = ConversationKey(chat_id=200, user_id=1)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def test_history_survives_a_new_repository_instance(self) -> None:
        first = SQLiteConversationRepository(self.database_path)
        first.append(
            self.key,
            Message(role=Role.USER, content="Hello"),
        )
        first.append(
            self.key,
            Message(role=Role.ASSISTANT, content="Hi"),
        )

        restored = SQLiteConversationRepository(self.database_path)

        self.assertEqual(
            restored.history(self.key),
            [
                Message(role=Role.USER, content="Hello"),
                Message(role=Role.ASSISTANT, content="Hi"),
            ],
        )

    def test_history_is_keyed_ordered_and_limited(self) -> None:
        repository = SQLiteConversationRepository(self.database_path)
        for content in ("first", "second", "third"):
            repository.append(
                self.key,
                Message(role=Role.USER, content=content),
            )
        repository.append(
            self.other_key,
            Message(role=Role.USER, content="other"),
        )

        self.assertEqual(
            [message.content for message in repository.history(self.key)],
            ["first", "second", "third"],
        )
        self.assertEqual(
            [message.content for message in repository.history(self.key, limit=2)],
            ["second", "third"],
        )
        self.assertEqual(
            [message.content for message in repository.history(self.other_key)],
            ["other"],
        )

    def test_clear_affects_only_selected_conversation(self) -> None:
        repository = SQLiteConversationRepository(self.database_path)
        for key in (self.key, self.other_key):
            repository.append(
                key,
                Message(role=Role.USER, content=str(key.chat_id)),
            )

        repository.clear(self.key)

        self.assertEqual(repository.history(self.key), [])
        self.assertEqual(
            [message.content for message in repository.history(self.other_key)],
            ["200"],
        )

    def test_system_messages_are_rejected_and_not_persisted(self) -> None:
        repository = SQLiteConversationRepository(self.database_path)

        with self.assertRaisesRegex(ValueError, "System messages"):
            repository.append(
                self.key,
                Message(role=Role.SYSTEM, content="Never persist this"),
            )

        self.assertEqual(repository.history(self.key), [])

    def test_message_serialization_preserves_supported_roles_and_content(self) -> None:
        repository = SQLiteConversationRepository(self.database_path)
        messages = [
            Message(role=Role.USER, content="Привет"),
            Message(role=Role.ASSISTANT, content="Ответ"),
            Message(role=Role.TOOL, content='{"temperature": 20}'),
        ]
        for message in messages:
            repository.append(self.key, message)

        self.assertEqual(repository.history(self.key), messages)

    def test_schema_uses_wal_and_utc_timestamps(self) -> None:
        SQLiteConversationRepository(self.database_path).append(
            self.key,
            Message(role=Role.USER, content="Hello"),
        )

        connection = sqlite3.connect(self.database_path)
        try:
            journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
            timestamp = connection.execute(
                "SELECT created_at_utc FROM conversation_messages"
            ).fetchone()[0]
        finally:
            connection.close()

        self.assertEqual(journal_mode.lower(), "wal")
        self.assertEqual(
            datetime.fromisoformat(timestamp).tzinfo,
            timezone.utc,
        )
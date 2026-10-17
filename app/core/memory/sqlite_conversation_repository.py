from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Sequence

from app.core.memory.base_memory import BaseMemory
from app.core.models import ConversationKey, Message, Role


class SQLiteConversationRepository(BaseMemory):
    """SQLite-backed short-term conversation history."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        busy_timeout_ms: int = 5_000,
    ) -> None:
        database_file = Path(database_path)
        database_file.parent.mkdir(parents=True, exist_ok=True)
        self._database_path = str(database_file)
        self._busy_timeout_ms = busy_timeout_ms
        self._initialize()

    def append(self, key: ConversationKey, message: Message) -> None:
        role, content = self._serialize(message)
        created_at_utc = datetime.now(timezone.utc).isoformat()

        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO conversation_messages (
                    chat_id,
                    user_id,
                    role,
                    content,
                    created_at_utc
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    key.chat_id,
                    key.user_id,
                    role,
                    content,
                    created_at_utc,
                ),
            )

    def history(
        self,
        key: ConversationKey,
        limit: int | None = None,
    ) -> list[Message]:
        if limit == 0:
            return []

        with self._connection() as connection:
            if limit is None:
                rows = connection.execute(
                    """
                    SELECT role, content
                    FROM conversation_messages
                    WHERE chat_id = ? AND user_id = ?
                    ORDER BY id ASC
                    """,
                    (key.chat_id, key.user_id),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT role, content
                    FROM (
                        SELECT id, role, content
                        FROM conversation_messages
                        WHERE chat_id = ? AND user_id = ?
                        ORDER BY id DESC
                        LIMIT ?
                    )
                    ORDER BY id ASC
                    """,
                    (key.chat_id, key.user_id, limit),
                ).fetchall()

        return [self._deserialize(row) for row in rows]

    def clear(self, key: ConversationKey) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                DELETE FROM conversation_messages
                WHERE chat_id = ? AND user_id = ?
                """,
                (key.chat_id, key.user_id),
            )

    def trim(self, key: ConversationKey, max_messages: int) -> None:
        """Remove the oldest messages beyond one conversation's limit."""
        with self._connection() as connection:
            connection.execute(
                """
                DELETE FROM conversation_messages
                WHERE id IN (
                    SELECT id
                    FROM conversation_messages
                    WHERE chat_id = ? AND user_id = ?
                    ORDER BY id DESC
                    LIMIT -1 OFFSET ?
                )
                """,
                (key.chat_id, key.user_id, max_messages),
            )

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL
                        CHECK (role IN ('user', 'assistant', 'tool')),
                    content TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_conversation_messages_key_order
                ON conversation_messages (chat_id, user_id, id)
                """
            )

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._database_path)
        connection.execute(f"PRAGMA busy_timeout = {self._busy_timeout_ms}")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _serialize(message: Message) -> tuple[str, str]:
        if message.role is Role.SYSTEM:
            raise ValueError("System messages are not conversation memory.")

        return message.role.value, message.content

    @staticmethod
    def _deserialize(row: tuple[str, str]) -> Message:
        role, content = row
        return Message(role=Role(role), content=content)
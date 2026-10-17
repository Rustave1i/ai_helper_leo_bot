"""Standalone async SQLite group journal; importing this module performs no I/O."""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import fields
from pathlib import Path
import sqlite3
import time
from typing import Callable, Iterator, TypeVar

from .models import (
    GroupChat, GroupMessageEvent, IngestResult, JournalMessage, integer,
)

T = TypeVar("T")
DAY_MS = 86_400_000
_EVENT_COLUMNS = tuple(field.name for field in fields(GroupMessageEvent))
_RECEIPT_COLUMNS = (
    "first_received_at_utc_ms", "revision_received_at_utc_ms", "first_seen_as",
)
_CHAT_COLUMNS = (
    "chat_id", "timezone", "retention_days", "observation_started_at",
    "collect_after", "enabled",
)
_SCHEMA = (
    """CREATE TABLE group_chats (
        chat_id INTEGER PRIMARY KEY,
        enabled INTEGER NOT NULL DEFAULT 0 CHECK(enabled IN (0,1)),
        timezone TEXT NOT NULL CHECK(length(timezone) > 0),
        retention_days INTEGER NOT NULL CHECK(retention_days > 0),
        observation_started_at INTEGER NOT NULL CHECK(observation_started_at >= 0),
        collect_after INTEGER NOT NULL CHECK(collect_after >= observation_started_at)
    )""",
    """CREATE TABLE group_messages (
        chat_id INTEGER NOT NULL REFERENCES group_chats(chat_id),
        message_id INTEGER NOT NULL CHECK(message_id > 0),
        thread_id INTEGER NOT NULL CHECK(thread_id >= 0),
        sender_kind TEXT NOT NULL CHECK(sender_kind IN ('user','chat','unknown')),
        text TEXT NOT NULL,
        sent_at_utc_ms INTEGER NOT NULL CHECK(sent_at_utc_ms >= 0),
        source_update_id INTEGER NOT NULL CHECK(source_update_id >= 0),
        sender_user_id INTEGER,
        sender_chat_id INTEGER,
        display_name TEXT,
        author_signature TEXT,
        sender_is_bot INTEGER CHECK(sender_is_bot IN (0,1)),
        edited_at_utc_ms INTEGER CHECK(edited_at_utc_ms >= sent_at_utc_ms),
        reply_to_message_id INTEGER CHECK(reply_to_message_id > 0),
        first_received_at_utc_ms INTEGER NOT NULL,
        revision_received_at_utc_ms INTEGER NOT NULL,
        first_seen_as TEXT NOT NULL CHECK(first_seen_as IN ('message','edit')),
        PRIMARY KEY(chat_id, message_id),
        CHECK (
            (sender_kind='user' AND sender_user_id IS NOT NULL
                AND sender_user_id > 0 AND sender_chat_id IS NULL) OR
            (sender_kind='chat' AND sender_chat_id IS NOT NULL
                AND sender_user_id IS NULL) OR
            (sender_kind='unknown' AND sender_user_id IS NULL
                AND sender_chat_id IS NULL)
        )
    )""",
    """CREATE INDEX group_messages_scope_time
        ON group_messages(chat_id, thread_id, sent_at_utc_ms, message_id)""",
    "CREATE INDEX group_messages_retention ON group_messages(sent_at_utc_ms)",
)


class SQLiteGroupJournal:
    """One-use lifecycle on one event loop.

    Cancellation of a caller does not cancel a submitted SQLite operation.
    close() drains it before shutting down the single worker. No autonomous
    collection, cleanup scheduler, response queue, or global config is used.
    """

    def __init__(
        self, database_path: str | Path, *,
        clock: Callable[[], int] | None = None, busy_timeout_ms: int = 1_000,
    ) -> None:
        integer(busy_timeout_ms, "busy_timeout_ms", 0)
        self._path = Path(database_path)
        self._clock = clock or (lambda: time.time_ns() // 1_000_000)
        self._busy_timeout_ms = busy_timeout_ms
        self._executor: ThreadPoolExecutor | None = None
        self._pending: set[asyncio.Future] = set()
        self._state = "new"
        self._opening: asyncio.Task | None = None
        self._closing: asyncio.Task | None = None

    async def open(self) -> None:
        if self._state == "new":
            self._state = "opening"
            self._executor = ThreadPoolExecutor(
                max_workers=1, thread_name_prefix="group-journal",
            )
            self._opening = asyncio.create_task(self._finish_open())
            self._opening.add_done_callback(self._observe)
        if self._state not in ("opening", "open"):
            raise RuntimeError("Journal cannot be opened in its current state")
        await asyncio.shield(self._opening)

    async def _finish_open(self) -> None:
        try:
            await self._submit(self._initialize)
        except BaseException:
            await self._shutdown_executor()
            if self._state != "closing":
                self._state = "closed"
            raise
        if self._state == "opening":
            self._state = "open"

    @staticmethod
    def _observe(future: asyncio.Future) -> None:
        # Retrieve failures even when the original awaiter has been cancelled.
        if not future.cancelled():
            future.exception()

    async def _shutdown_executor(self) -> None:
        executor = self._executor
        if executor is not None:
            await asyncio.to_thread(executor.shutdown, wait=True)
            self._executor = None

    async def close(self) -> None:
        if self._closing is None:
            self._state = "closing"
            self._closing = asyncio.create_task(self._finish_close())
            self._closing.add_done_callback(self._observe)
        await asyncio.shield(self._closing)

    async def _finish_close(self) -> None:
        if self._opening is not None:
            await asyncio.gather(self._opening, return_exceptions=True)
        if self._pending:
            await asyncio.gather(*tuple(self._pending), return_exceptions=True)
        await self._shutdown_executor()
        self._state = "closed"

    async def _submit(self, function: Callable[..., T], *args) -> T:
        if self._executor is None:
            raise RuntimeError("Journal worker is not available")
        # submit happens before the first await; shield protects the real work.
        future = asyncio.wrap_future(self._executor.submit(function, *args))
        self._pending.add(future)

        def finished(done: asyncio.Future) -> None:
            self._pending.discard(done)
            self._observe(done)

        future.add_done_callback(finished)
        return await asyncio.shield(future)

    async def _run(self, function: Callable[..., T], *args) -> T:
        if self._state != "open":
            raise RuntimeError("Journal is not open")
        return await self._submit(function, *args)

    def _now(self) -> int:
        value = self._clock()
        integer(value, "clock", 0)
        return value

    @contextmanager
    def _connection(self, *, write: bool) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(
            self._path, timeout=self._busy_timeout_ms / 1_000, isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection(write=True) as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            tables = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "AND name NOT LIKE 'sqlite_%'"
                )
            }
            if version == 0 and not tables:
                for statement in _SCHEMA:
                    connection.execute(statement)
                connection.execute("PRAGMA user_version=1")
            elif version != 1 or tables != {"group_chats", "group_messages"}:
                raise RuntimeError("Unsupported group journal schema")
            else:
                for table, expected in (
                    ("group_chats", _CHAT_COLUMNS),
                    ("group_messages", _EVENT_COLUMNS + _RECEIPT_COLUMNS),
                ):
                    # Only literal internal table names enter this PRAGMA.
                    actual = {
                        row[1] for row in connection.execute(f"PRAGMA table_info({table})")
                    }
                    if actual != set(expected):
                        raise RuntimeError("Group journal columns do not match version 1")
        # WAL cannot be changed inside the schema transaction.
        connection = sqlite3.connect(
            self._path, timeout=self._busy_timeout_ms / 1_000, isolation_level=None,
        )
        try:
            connection.execute("PRAGMA journal_mode=WAL")
        finally:
            connection.close()

    async def configure_chat(
        self, chat_id: int, *, timezone: str, retention_days: int,
        enabled: bool = False,
    ) -> GroupChat:
        integer(chat_id, "chat_id")
        integer(retention_days, "retention_days", 1)
        if not isinstance(timezone, str) or not timezone.strip():
            raise ValueError("timezone must be a nonempty stored setting")
        if type(enabled) is not bool:
            raise ValueError("enabled must be bool")
        return await self._run(
            self._configure_chat, chat_id, timezone, retention_days, enabled,
        )

    def _configure_chat(self, chat_id, timezone, retention_days, enabled) -> GroupChat:
        now = self._now()
        with self._connection(write=True) as connection:
            connection.execute(
                """INSERT INTO group_chats (
                    chat_id, timezone, retention_days, enabled,
                    observation_started_at, collect_after
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET timezone=excluded.timezone,
                    retention_days=excluded.retention_days, enabled=excluded.enabled""",
                (chat_id, timezone, retention_days, enabled, now, now),
            )
            return self._chat(connection, chat_id)

    @staticmethod
    def _chat(connection, chat_id) -> GroupChat | None:
        row = connection.execute(
            "SELECT * FROM group_chats WHERE chat_id=?", (chat_id,),
        ).fetchone()
        if row is None:
            return None
        return GroupChat(**{**dict(row), "enabled": bool(row["enabled"])})

    async def get_chat(self, chat_id: int) -> GroupChat | None:
        integer(chat_id, "chat_id")
        return await self._run(self._get_chat, chat_id)

    def _get_chat(self, chat_id):
        with self._connection(write=False) as connection:
            return self._chat(connection, chat_id)

    @staticmethod
    def _message(row) -> JournalMessage:
        values = {name: row[name] for name in _EVENT_COLUMNS}
        if values["sender_is_bot"] is not None:
            values["sender_is_bot"] = bool(values["sender_is_bot"])
        return JournalMessage(
            GroupMessageEvent(**values),
            **{name: row[name] for name in _RECEIPT_COLUMNS},
        )

    @staticmethod
    def _version(event: GroupMessageEvent) -> tuple:
        return (
            event.edited_at_utc_ms is not None,
            event.edited_at_utc_ms or 0, event.source_update_id,
        )

    async def ingest(self, event: GroupMessageEvent) -> IngestResult:
        if not isinstance(event, GroupMessageEvent):
            raise TypeError("event must be GroupMessageEvent")
        return await self._run(self._ingest, event)

    def _ingest(self, event) -> IngestResult:
        now = self._now()
        with self._connection(write=True) as connection:
            chat = self._chat(connection, event.chat_id)
            if (
                chat is None or not chat.enabled
                or event.sent_at_utc_ms <= chat.collect_after
                or event.sent_at_utc_ms < chat.observation_started_at
                or event.sent_at_utc_ms < now - chat.retention_days * DAY_MS
            ):
                return IngestResult.REJECTED
            row = connection.execute(
                "SELECT * FROM group_messages WHERE chat_id=? AND message_id=?",
                (event.chat_id, event.message_id),
            ).fetchone()
            if row is not None:
                previous = self._message(row).event
                identity = (
                    "thread_id", "sent_at_utc_ms", "sender_kind", "sender_user_id",
                    "sender_chat_id", "sender_is_bot",
                )
                if any(getattr(event, k) != getattr(previous, k) for k in identity):
                    return IngestResult.CONFLICT
                if self._version(event) < self._version(previous):
                    return IngestResult.STALE
                if self._version(event) == self._version(previous):
                    return (
                        IngestResult.DUPLICATE if event == previous
                        else IngestResult.CONFLICT
                    )
                assignments = ", ".join(f"{name}=?" for name in _EVENT_COLUMNS)
                connection.execute(
                    f"UPDATE group_messages SET {assignments}, "
                    "revision_received_at_utc_ms=? WHERE chat_id=? AND message_id=?",
                    (*[getattr(event, name) for name in _EVENT_COLUMNS],
                     now, event.chat_id, event.message_id),
                )
                return IngestResult.UPDATED
            columns = _EVENT_COLUMNS + _RECEIPT_COLUMNS
            placeholders = ", ".join("?" for _ in columns)
            connection.execute(
                f"INSERT INTO group_messages ({', '.join(columns)}) "
                f"VALUES ({placeholders})",
                (*[getattr(event, name) for name in _EVENT_COLUMNS],
                 now, now, "edit" if event.edited_at_utc_ms is not None else "message"),
            )
            return IngestResult.INSERTED

    async def read_messages(
        self, chat_id: int, thread_id: int, *, limit: int,
    ) -> list[JournalMessage]:
        integer(chat_id, "chat_id")
        integer(thread_id, "thread_id", 0)
        integer(limit, "limit", 0)
        return await self._run(self._read_messages, chat_id, thread_id, limit)

    def _read_messages(self, chat_id, thread_id, limit):
        now = self._now()
        with self._connection(write=False) as connection:
            rows = connection.execute(
                """SELECT * FROM (
                    SELECT m.* FROM group_messages m JOIN group_chats c
                        ON c.chat_id=m.chat_id
                    WHERE m.chat_id=? AND m.thread_id=? AND c.enabled=1
                        AND m.sent_at_utc_ms > c.collect_after
                        AND m.sent_at_utc_ms >= c.observation_started_at
                        AND m.sent_at_utc_ms >= ? - c.retention_days * ?
                    ORDER BY m.sent_at_utc_ms DESC, m.message_id DESC LIMIT ?
                ) ORDER BY sent_at_utc_ms ASC, message_id ASC""",
                (chat_id, thread_id, now, DAY_MS, limit),
            ).fetchall()
            return [self._message(row) for row in rows]

    async def purge_expired(self) -> int:
        return await self._run(self._purge_expired)

    def _purge_expired(self):
        now = self._now()
        with self._connection(write=True) as connection:
            return connection.execute(
                """DELETE FROM group_messages WHERE EXISTS (
                    SELECT 1 FROM group_chats c WHERE c.chat_id=group_messages.chat_id
                    AND group_messages.sent_at_utc_ms < ? - c.retention_days * ?
                )""", (now, DAY_MS),
            ).rowcount

    async def delete_archive(self, chat_id: int) -> int:
        integer(chat_id, "chat_id")
        return await self._run(self._delete_archive, chat_id)

    def _delete_archive(self, chat_id):
        now = self._now()
        with self._connection(write=True) as connection:
            connection.execute(
                "UPDATE group_chats SET collect_after=MAX(collect_after, ?, "
                "COALESCE((SELECT MAX(sent_at_utc_ms) FROM group_messages "
                "WHERE chat_id=?), collect_after)) WHERE chat_id=?",
                (now, chat_id, chat_id),
            )
            return connection.execute(
                "DELETE FROM group_messages WHERE chat_id=?", (chat_id,),
            ).rowcount

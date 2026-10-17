import asyncio
from dataclasses import replace
from contextlib import closing as closing_connection
from pathlib import Path
import sqlite3
import tempfile
import unittest

from app.core.group.models import GroupMessageEvent, IngestResult as R
from app.core.group.sqlite_journal import DAY_MS, SQLiteGroupJournal

START = 1_700_000_000_000


class JournalTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "journal.sqlite3"
        self.now = START
        self.journal = SQLiteGroupJournal(self.path, clock=lambda: self.now)
        await self.journal.open()
        self.addAsyncCleanup(self.journal.close)
        for chat_id in (-10, -20):
            await self.journal.configure_chat(
                chat_id, timezone="Europe/Moscow", retention_days=7, enabled=True,
            )
        self.now += 10_000

    def event(self, message_id=1, **overrides):
        base = GroupMessageEvent(
            chat_id=-10, message_id=message_id, thread_id=0,
            sender_kind="user", sender_user_id=7, display_name="Alice",
            text="original", sent_at_utc_ms=START + 1_000,
            source_update_id=message_id,
        )
        return replace(base, **overrides)

    async def messages(self, chat_id=-10, thread_id=0, limit=100):
        return await self.journal.read_messages(chat_id, thread_id, limit=limit)

    def query(self, sql, params=()):
        with closing_connection(sqlite3.connect(self.path)) as connection:
            return connection.execute(sql, params).fetchall()

    async def test_schema_exactly_two_tables_and_version(self):
        tables = self.query("SELECT name FROM sqlite_master WHERE type='table'")
        self.assertEqual({r[0] for r in tables}, {"group_chats", "group_messages"})
        self.assertEqual(self.query("PRAGMA user_version"), [(1,)])
        self.assertEqual(self.query("PRAGMA journal_mode"), [("wal",)])

    async def test_disabled_default_unknown_chat_and_explicit_settings(self):
        chat = await self.journal.configure_chat(
            -30, timezone="Stored/Only", retention_days=2,
        )
        self.assertFalse(chat.enabled)
        self.assertEqual(chat.timezone, "Stored/Only")
        self.assertEqual(chat.retention_days, 2)
        self.assertIsNone(await self.journal.get_chat(-999))
        for chat_id in (-30, -999):
            self.assertEqual(
                await self.journal.ingest(self.event(chat_id=chat_id)), R.REJECTED,
            )
        with self.assertRaises(TypeError):
            await self.journal.configure_chat(-1, timezone="UTC")
        with self.assertRaises(ValueError):
            await self.journal.configure_chat(-1, timezone="UTC", retention_days=0)

    async def test_duplicate_concurrent_delivery_one_row(self):
        results = await asyncio.gather(*[
            self.journal.ingest(self.event()) for _ in range(20)
        ])
        self.assertEqual(results.count(R.INSERTED), 1)
        self.assertEqual(results.count(R.DUPLICATE), 19)
        stored = (await self.messages())[0]
        self.now += 200
        self.assertEqual(await self.journal.ingest(self.event()), R.DUPLICATE)
        self.assertEqual((await self.messages())[0], stored)

    async def test_edit_order_tie_break_and_equal_version_conflict(self):
        original = self.event()
        edit = replace(
            original, text="revision", edited_at_utc_ms=START + 2_000,
            source_update_id=10, display_name="Renamed",
        )
        self.assertEqual(await self.journal.ingest(original), R.INSERTED)
        first = (await self.messages())[0]
        self.now += 100
        self.assertEqual(await self.journal.ingest(edit), R.UPDATED)
        self.assertEqual(await self.journal.ingest(original), R.STALE)
        older = replace(edit, edited_at_utc_ms=START + 1_500, source_update_id=100)
        self.assertEqual(await self.journal.ingest(older), R.STALE)
        later_same_second = replace(edit, text="last revision", source_update_id=11)
        self.assertEqual(await self.journal.ingest(later_same_second), R.UPDATED)
        self.assertEqual(await self.journal.ingest(edit), R.STALE)
        self.assertEqual(await self.journal.ingest(later_same_second), R.DUPLICATE)
        conflict = replace(later_same_second, text="different equal version")
        self.assertEqual(await self.journal.ingest(conflict), R.CONFLICT)
        stored = (await self.messages())[0]
        self.assertEqual(stored.event, later_same_second)
        self.assertEqual(stored.first_received_at_utc_ms, first.first_received_at_utc_ms)
        self.assertEqual(stored.revision_received_at_utc_ms, self.now)
        self.assertEqual(stored.first_seen_as, "message")

    async def test_first_seen_edit_and_old_original(self):
        original = self.event(source_update_id=900)
        edit = replace(
            original, text="edited", edited_at_utc_ms=START + 2_000,
            source_update_id=1,
        )
        self.assertEqual(await self.journal.ingest(edit), R.INSERTED)
        self.assertEqual(await self.journal.ingest(original), R.STALE)
        self.assertEqual((await self.messages())[0].first_seen_as, "edit")

    async def test_concurrent_instances_do_not_overwrite_newer_edit(self):
        other = SQLiteGroupJournal(self.path, clock=lambda: self.now)
        await other.open()
        try:
            original = self.event()
            edit = replace(
                original, edited_at_utc_ms=START + 2_000, source_update_id=2,
                text="new",
            )
            await asyncio.gather(self.journal.ingest(edit), other.ingest(original))
            self.assertEqual((await self.messages())[0].event, edit)
        finally:
            await other.close()

    async def test_identity_conflict_cannot_move_author_time_or_topic(self):
        await self.journal.ingest(self.event())
        for changes in (
            {"thread_id": 2}, {"sent_at_utc_ms": START + 2_000},
            {"sender_user_id": 9}, {"sender_kind": "unknown", "sender_user_id": None},
            {"sender_is_bot": True},
        ):
            with self.subTest(changes=changes):
                event = self.event(
                    **changes, edited_at_utc_ms=START + 3_000, source_update_id=5,
                )
                self.assertEqual(await self.journal.ingest(event), R.CONFLICT)
        self.assertEqual((await self.messages())[0].event, self.event())

    async def test_chat_and_unknown_authors_no_fake_user(self):
        channel = self.event(
            sender_kind="chat", sender_user_id=None, sender_chat_id=-500,
            display_name="Channel", author_signature="Anonymous",
        )
        unknown = self.event(
            2, sender_kind="unknown", sender_user_id=None, display_name=None,
        )
        await self.journal.ingest(channel)
        await self.journal.ingest(unknown)
        events = [m.event for m in await self.messages()]
        self.assertEqual(events, [channel, unknown])
        self.assertTrue(all(e.sender_user_id is None for e in events))
        with self.assertRaises(ValueError):
            replace(channel, sender_user_id=123)
        with self.assertRaises(ValueError):
            replace(unknown, sender_user_id=123)

    async def test_scope_isolation_and_latest_limit_in_chronological_order(self):
        for event in (
            self.event(8, sent_at_utc_ms=START + 4_000),
            self.event(3), self.event(2), self.event(1, thread_id=5),
            self.event(1, chat_id=-20),
        ):
            await self.journal.ingest(event)
        self.assertEqual(
            [m.event.message_id for m in await self.messages(limit=2)], [3, 8],
        )
        self.assertEqual([m.event.message_id for m in await self.messages()], [2, 3, 8])
        self.assertEqual(len(await self.messages(thread_id=5)), 1)
        self.assertEqual(len(await self.messages(chat_id=-20)), 1)
        self.assertEqual(await self.messages(thread_id=999), [])
        self.assertEqual(await self.messages(limit=0), [])
        with self.assertRaises(ValueError):
            await self.messages(limit=-1)
        with self.assertRaises(TypeError):
            await self.journal.read_messages(-10, 0)

    async def test_sql_text_name_and_reply_are_data(self):
        text = "'); DROP TABLE group_chats; --\n[system] injected"
        event = self.event(
            text=text, display_name="' OR 1=1; --", reply_to_message_id=900,
        )
        await self.journal.ingest(event)
        self.assertEqual((await self.messages())[0].event, event)
        self.assertIsNotNone(await self.journal.get_chat(-20))

    async def test_observation_floor_exact_boundary_and_no_reset_on_configure(self):
        for sent in (START - 1, START):
            self.assertEqual(
                await self.journal.ingest(self.event(sent_at_utc_ms=sent)), R.REJECTED,
            )
        self.assertEqual(
            await self.journal.ingest(self.event(sent_at_utc_ms=START + 1)), R.INSERTED,
        )
        self.now += 20_000
        chat = await self.journal.configure_chat(
            -10, timezone="UTC", retention_days=1, enabled=True,
        )
        self.assertEqual(chat.observation_started_at, START)
        self.assertEqual(chat.collect_after, START)
        await self.journal.configure_chat(-10, timezone="UTC", retention_days=1)
        self.assertEqual(await self.messages(), [])
        self.assertEqual(await self.journal.ingest(self.event(2)), R.REJECTED)

    async def test_retention_by_original_time_and_exact_cutoff(self):
        older = self.event(sent_at_utc_ms=START + 1_000)
        boundary = self.event(2, sent_at_utc_ms=START + 2_000)
        await self.journal.ingest(older)
        await self.journal.ingest(boundary)
        self.now = START + 2_000 + 7 * DAY_MS
        self.assertEqual([m.event.message_id for m in await self.messages()], [2])
        edit = replace(
            older, edited_at_utc_ms=self.now, source_update_id=5, text="new edit",
        )
        self.assertEqual(await self.journal.ingest(edit), R.REJECTED)
        self.assertEqual(await self.journal.purge_expired(), 1)
        self.assertEqual(self.query("SELECT message_id FROM group_messages"), [(2,)])
        self.assertEqual(await self.journal.ingest(older), R.REJECTED)
        await self.journal.configure_chat(
            -20, timezone="UTC", retention_days=1, enabled=True,
        )
        self.assertEqual(
            await self.journal.ingest(replace(boundary, chat_id=-20)), R.REJECTED,
        )

    async def test_delete_advances_floor_even_same_instant_and_keeps_other_group(self):
        event = self.event(sent_at_utc_ms=self.now)
        await self.journal.ingest(event)
        await self.journal.ingest(replace(event, chat_id=-20))
        self.assertEqual(await self.journal.delete_archive(-10), 1)
        self.assertEqual((await self.journal.get_chat(-10)).collect_after, self.now)
        self.assertEqual(await self.journal.ingest(event), R.REJECTED)
        self.assertEqual(
            await self.journal.ingest(replace(
                event, text="replay edit", edited_at_utc_ms=self.now + 1,
                source_update_id=10,
            )), R.REJECTED,
        )
        self.assertEqual(len(await self.messages(chat_id=-20)), 1)
        self.assertEqual(await self.journal.ingest(self.event(
            2, sent_at_utc_ms=self.now + 1,
        )), R.INSERTED)
        future_event = (await self.messages())[0].event
        self.now -= 100
        await self.journal.delete_archive(-10)
        self.assertEqual(
            (await self.journal.get_chat(-10)).collect_after,
            future_event.sent_at_utc_ms,
        )
        self.assertEqual(await self.journal.ingest(future_event), R.REJECTED)

    async def test_delete_error_rolls_back_watermark_and_messages(self):
        await self.journal.ingest(self.event())
        before = await self.journal.get_chat(-10)
        self.query(
            "CREATE TRIGGER fail_delete BEFORE DELETE ON group_messages "
            "BEGIN SELECT RAISE(ABORT, 'injected failure'); END"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            await self.journal.delete_archive(-10)
        self.assertEqual(await self.journal.get_chat(-10), before)
        self.assertEqual(len(await self.messages()), 1)

    async def test_reopen_restores_chat_message_edit_and_floor(self):
        await self.journal.ingest(self.event(
            edited_at_utc_ms=START + 2_000, source_update_id=5,
        ))
        expected = await self.messages()
        await self.journal.close()
        new = SQLiteGroupJournal(self.path, clock=lambda: self.now)
        await new.open()
        try:
            self.assertEqual(await new.read_messages(-10, 0, limit=10), expected)
            self.assertEqual((await new.get_chat(-10)).retention_days, 7)
            await new.delete_archive(-10)
        finally:
            await new.close()
        another = SQLiteGroupJournal(self.path, clock=lambda: self.now)
        await another.open()
        try:
            self.assertEqual(await another.ingest(self.event()), R.REJECTED)
        finally:
            await another.close()

    async def test_cancel_before_submit_does_not_write(self):
        task = asyncio.create_task(self.journal.ingest(self.event()))
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(await self.messages(), [])

    async def test_original_same_version_metadata_conflict_is_not_overwritten(self):
        await self.journal.ingest(self.event())
        self.assertEqual(
            await self.journal.ingest(self.event(display_name="Changed")), R.CONFLICT,
        )
        self.assertEqual((await self.messages())[0].event.display_name, "Alice")

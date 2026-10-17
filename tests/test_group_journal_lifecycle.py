import asyncio
from contextlib import closing as closing_connection
from pathlib import Path
import os
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from app.core.group.models import GroupMessageEvent, IngestResult
from app.core.group.sqlite_journal import SQLiteGroupJournal

START = 1_700_000_000_000


async def wait_event(event):
    for _ in range(1_000):
        if event.is_set():
            return
        await asyncio.sleep(0.002)
    raise AssertionError("Worker did not enter the operation")


class JournalLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "journal.sqlite3"
        self.journal = SQLiteGroupJournal(self.path, clock=lambda: START)
        await self.journal.open()
        self.addAsyncCleanup(self.journal.close)
        await self.journal.configure_chat(
            -10, timezone="UTC", retention_days=7, enabled=True,
        )
        self.event = GroupMessageEvent(
            -10, 1, 0, "unknown", "offline", START + 1, 1,
        )

    def test_import_and_constructor_do_not_create_files_or_workers(self):
        folder = Path(self.temp.name) / "import-only"
        folder.mkdir()
        root = str(Path(__file__).resolve().parents[1])
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONPATH"] = os.pathsep.join(
            p for p in (root, env.get("PYTHONPATH")) if p
        )
        code = (
            "import os,threading; "
            "from app.core.group.sqlite_journal import SQLiteGroupJournal; "
            "j=SQLiteGroupJournal('nested/unopened.sqlite3'); "
            "assert os.listdir('.')==[]; "
            "assert not any(t.name.startswith('group-journal') "
            "for t in threading.enumerate())"
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", code], cwd=folder, env=env,
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    async def test_close_before_open_is_idempotent_and_no_io(self):
        path = Path(self.temp.name) / "never" / "opened.sqlite3"
        journal = SQLiteGroupJournal(path)
        await journal.close()
        await journal.close()
        self.assertFalse(path.parent.exists())
        with self.assertRaises(RuntimeError):
            await journal.open()

    async def test_calls_before_open_and_after_close_fail(self):
        journal = SQLiteGroupJournal(Path(self.temp.name) / "other.sqlite3")
        with self.assertRaises(RuntimeError):
            await journal.ingest(self.event)
        await self.journal.close()
        with self.assertRaises(RuntimeError):
            await self.journal.ingest(self.event)
        with self.assertRaises(RuntimeError):
            await self.journal.open()

    async def test_concurrent_open_and_close_drain_accepted_operations(self):
        await asyncio.gather(self.journal.open(), self.journal.open())
        operation = asyncio.create_task(self.journal.ingest(self.event))
        await asyncio.sleep(0)
        closing = asyncio.create_task(self.journal.close())
        self.assertEqual(await operation, IngestResult.INSERTED)
        await closing
        self.assertIsNone(self.journal._executor)
        self.assertEqual(len(self.journal._pending), 0)

    async def test_sqlite_contention_keeps_event_loop_responsive(self):
        journal = SQLiteGroupJournal(
            self.path, clock=lambda: START + 10, busy_timeout_ms=150,
        )
        await journal.open()
        self.addAsyncCleanup(journal.close)
        locker = sqlite3.connect(self.path)
        locker.execute("BEGIN IMMEDIATE")
        entered = threading.Event()
        real_connect = sqlite3.connect

        class Connection(sqlite3.Connection):
            def execute(self, sql, parameters=()):
                if sql == "BEGIN IMMEDIATE":
                    entered.set()
                return super().execute(sql, parameters)

        def connect(*args, **kwargs):
            return real_connect(*args, **kwargs, factory=Connection)

        try:
            with patch(
                "app.core.group.sqlite_journal.sqlite3.connect", side_effect=connect,
            ):
                task = asyncio.create_task(journal.ingest(self.event))
                await wait_event(entered)
                ticks = 0
                while not task.done():
                    await asyncio.sleep(0.005)
                    ticks += 1
                with self.assertRaises(sqlite3.OperationalError):
                    await task
                self.assertGreater(ticks, 2)
        finally:
            locker.rollback()
            locker.close()
        self.assertEqual(
            await journal.read_messages(-10, 0, limit=10), [],
        )

    async def test_cancelled_ingest_and_cancelled_close_drain_commit(self):
        self.journal._busy_timeout_ms = 2_000
        locker = sqlite3.connect(self.path)
        locker.execute("BEGIN IMMEDIATE")
        entered = threading.Event()
        real_connect = sqlite3.connect
        resources = []
        worker_threads = set()

        class Connection(sqlite3.Connection):
            def execute(self, sql, parameters=()):
                worker_threads.add(threading.current_thread())
                if sql == "BEGIN IMMEDIATE":
                    entered.set()
                return super().execute(sql, parameters)

            def close(self):
                resources.append("close")
                return super().close()

        def connect(*args, **kwargs):
            resources.append("open")
            return real_connect(*args, **kwargs, factory=Connection)

        try:
            with patch(
                "app.core.group.sqlite_journal.sqlite3.connect", side_effect=connect,
            ):
                operation = asyncio.create_task(self.journal.ingest(self.event))
                await wait_event(entered)
                operation.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await operation
                closing = asyncio.create_task(self.journal.close())
                await asyncio.sleep(0.03)
                self.assertFalse(closing.done())
                closing.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await closing
                locker.rollback()
                locker.close()
                locker = None
                await self.journal.close()
        finally:
            if locker is not None:
                locker.rollback()
                locker.close()
        with closing_connection(real_connect(self.path)) as connection:
            count = connection.execute("SELECT COUNT(*) FROM group_messages").fetchone()[0]
        self.assertEqual(count, 1, "Cancellation did not imply rollback")
        self.assertEqual(resources.count("open"), resources.count("close"))
        self.assertTrue(worker_threads)
        self.assertTrue(all(t.ident != threading.get_ident() for t in worker_threads))
        self.assertTrue(all(not t.is_alive() for t in worker_threads))
        self.assertIsNone(self.journal._executor)
        self.assertFalse(self.journal._pending)

    async def test_cancelled_open_can_be_closed_without_lost_worker(self):
        path = Path(self.temp.name) / "opening.sqlite3"
        journal = SQLiteGroupJournal(path)
        self.addAsyncCleanup(journal.close)
        entered, release = threading.Event(), threading.Event()
        initialize = journal._initialize

        def delayed():
            entered.set()
            if not release.wait(2):
                raise RuntimeError("test release missing")
            initialize()

        with patch.object(journal, "_initialize", side_effect=delayed):
            task = asyncio.create_task(journal.open())
            try:
                await wait_event(entered)
                task.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await task
                closing = asyncio.create_task(journal.close())
                await asyncio.sleep(0)
                self.assertFalse(closing.done())
            finally:
                release.set()
            await closing
        self.assertIsNone(journal._executor)
        self.assertEqual(journal._state, "closed")

    async def test_commit_error_rolls_back_and_closes_connection(self):
        real_connect = sqlite3.connect
        events = []

        class Connection(sqlite3.Connection):
            def commit(self):
                raise sqlite3.OperationalError("injected commit failure")

            def rollback(self):
                events.append("rollback")
                return super().rollback()

            def close(self):
                events.append("close")
                return super().close()

        def connect(*args, **kwargs):
            return real_connect(*args, **kwargs, factory=Connection)

        with patch(
            "app.core.group.sqlite_journal.sqlite3.connect", side_effect=connect,
        ):
            with self.assertRaises(sqlite3.OperationalError):
                await self.journal.ingest(self.event)
        self.assertEqual(events, ["rollback", "close"])
        self.assertEqual(
            await self.journal.read_messages(-10, 0, limit=10), [],
        )

    async def test_unknown_or_unversioned_schema_is_not_migrated(self):
        for version in (0, 1, 77):
            with self.subTest(version=version):
                path = Path(self.temp.name) / f"bad-{version}.sqlite3"
                with closing_connection(sqlite3.connect(path)) as connection:
                    connection.execute("CREATE TABLE unrelated(value TEXT)")
                    connection.execute(f"PRAGMA user_version={version}")
                journal = SQLiteGroupJournal(path)
                try:
                    with self.assertRaises(RuntimeError):
                        await journal.open()
                    self.assertIsNone(journal._executor)
                finally:
                    await journal.close()
                with closing_connection(sqlite3.connect(path)) as connection:
                    self.assertEqual(
                        connection.execute("PRAGMA user_version").fetchone()[0], version,
                    )
                    self.assertEqual(
                        connection.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        ).fetchall(), [("unrelated",)],
                    )

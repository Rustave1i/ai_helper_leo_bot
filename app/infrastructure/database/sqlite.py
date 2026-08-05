from pathlib import Path
from typing import Any

import aiosqlite

from .database import Database


class SQLiteDatabase(Database):
    """Реализация Database для SQLite."""

    def __init__(
        self,
        database_path: Path,
    ) -> None:
        self._database_path = database_path
        self._connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        """Открывает соединение с SQLite."""

        self._connection = await aiosqlite.connect(self._database_path)
        self._connection.row_factory = aiosqlite.Row

        await self._connection.execute(
            "PRAGMA foreign_keys = ON;",
        )

    async def close(self) -> None:
        """Закрывает соединение."""

        if self._connection is None:
            return

        await self._connection.close()
        self._connection = None

    async def execute(
        self,
        query: str,
        parameters: tuple[Any, ...] = (),
    ) -> None:
        """Выполняет SQL-запрос без возврата результата."""

        connection = self._get_connection()

        await connection.execute(
            query,
            parameters,
        )

        await connection.commit()

    async def fetch_one(
        self,
        query: str,
        parameters: tuple[Any, ...] = (),
    ) -> dict[str, Any] | None:
        """Возвращает одну запись."""

        connection = self._get_connection()

        cursor = await connection.execute(
            query,
            parameters,
        )

        row = await cursor.fetchone()

        await cursor.close()

        if row is None:
            return None

        return dict(row)

    async def fetch_all(
        self,
        query: str,
        parameters: tuple[Any, ...] = (),
    ) -> list[dict[str, Any]]:
        """Возвращает список записей."""

        connection = self._get_connection()

        cursor = await connection.execute(
            query,
            parameters,
        )

        rows = await cursor.fetchall()

        await cursor.close()

        return [dict(row) for row in rows]

    async def execute_script(
        self,
        script: str,
    ) -> None:
        """Выполняет SQL-скрипт."""

        connection = self._get_connection()

        await connection.executescript(
            script,
        )

        await connection.commit()

    def _get_connection(
        self,
    ) -> aiosqlite.Connection:
        """Возвращает активное соединение."""

        if self._connection is None:
            raise RuntimeError(
                "Database connection is not established.",
            )

        return self._connection
from pathlib import Path

from .database import Database


class DatabaseInitializer:
    """Инициализирует базу данных."""

    def __init__(
        self,
        database: Database,
        schema_path: Path,
    ) -> None:
        self._database = database
        self._schema_path = schema_path

    async def initialize(self) -> None:
        """Создает структуру базы данных."""

        schema = self._schema_path.read_text(
            encoding="utf-8",
        )

        await self._database.execute_script(
            schema,
        )
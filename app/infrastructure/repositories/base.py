from app.infrastructure.database.database import Database


class BaseRepository:
    """Базовый класс для всех репозиториев."""

    def __init__(
        self,
        database: Database,
    ) -> None:
        self._database = database
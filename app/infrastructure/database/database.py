from abc import ABC, abstractmethod
from typing import Any


class Database(ABC):
    """Базовый интерфейс базы данных."""

    @abstractmethod
    async def connect(self) -> None:
        """Открывает соединение с БД."""
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Закрывает соединение с БД."""
        raise NotImplementedError

    @abstractmethod
    async def execute(
        self,
        query: str,
        parameters: tuple[Any, ...] = (),
    ) -> None:
        """Выполняет SQL-запрос без возврата результата."""
        raise NotImplementedError

    @abstractmethod
    async def fetch_one(
        self,
        query: str,
        parameters: tuple[Any, ...] = (),
    ) -> dict[str, Any] | None:
        """Возвращает одну запись."""
        raise NotImplementedError

    @abstractmethod
    async def fetch_all(
        self,
        query: str,
        parameters: tuple[Any, ...] = (),
    ) -> list[dict[str, Any]]:
        """Возвращает список записей."""
        raise NotImplementedError

    @abstractmethod
    async def execute_script(
        self,
        script: str,
    ) -> None:
        """Выполняет SQL-скрипт."""
        raise NotImplementedError
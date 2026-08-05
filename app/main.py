from pathlib import Path

import asyncio

from app.infrastructure.database.initializer import DatabaseInitializer
from app.infrastructure.database.sqlite import SQLiteDatabase


DATABASE_PATH = Path("data/leo.db")
SCHEMA_PATH = Path("app/infrastructure/database/schema.sql")


async def main() -> None:
    database = SQLiteDatabase(
        DATABASE_PATH,
    )

    await database.connect()

    initializer = DatabaseInitializer(
        database=database,
        schema_path=SCHEMA_PATH,
    )

    await initializer.initialize()

    await database.close()

    print("Leo database initialized.")


if __name__ == "__main__":
    asyncio.run(main())
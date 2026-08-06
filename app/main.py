from pathlib import Path
import asyncio

from app.adapters.telegram.bot import TelegramBot
from app.infrastructure.ai.factory import create_ai_client
from app.infrastructure.conversation_store import ConversationStore
from app.infrastructure.database.initializer import DatabaseInitializer
from app.infrastructure.database.sqlite import SQLiteDatabase
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.infrastructure.repositories.message_repository import MessageRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.leo.assistant import Assistant
from app.leo.prompt_builder import PromptBuilder
from app.leo.prompt_loader import PromptLoader


DATABASE_PATH = Path("data/leo.db")
SCHEMA_PATH = Path("app/infrastructure/database/schema.sql")
PROMPTS_PATH = Path("app/leo/prompts")


async def initialize() -> Assistant:
    database = SQLiteDatabase(
        DATABASE_PATH,
    )

    await database.connect()

    initializer = DatabaseInitializer(
        database=database,
        schema_path=SCHEMA_PATH,
    )

    await initializer.initialize()

    user_repository = UserRepository(
        database,
    )

    chat_repository = ChatRepository(
        database,
    )

    message_repository = MessageRepository(
        database,
    )

    conversation_store = ConversationStore(
        user_repository=user_repository,
        chat_repository=chat_repository,
        message_repository=message_repository,
    )

    prompt_loader = PromptLoader(
        PROMPTS_PATH,
    )

    prompt_builder = PromptBuilder(
        prompt_loader,
    )

    ai = create_ai_client()

    return (
        Assistant(
            prompt_builder=prompt_builder,
            ai=ai,
        ),
        conversation_store,
    )


def main() -> None:
    assistant = asyncio.run(
        initialize(),
    )

    bot = TelegramBot(
        assistant=assistant,
    )

    print("Leo started.")

    bot.run()


if __name__ == "__main__":
    main()
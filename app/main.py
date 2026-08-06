from pathlib import Path
import asyncio

from app.adapters.telegram.bot import TelegramBot
from app.infrastructure.ai.factory import create_ai_client
from app.infrastructure.conversation_store import ConversationStore
from app.infrastructure.database.initializer import DatabaseInitializer
from app.infrastructure.database.sqlite import SQLiteDatabase
from app.infrastructure.database.system_user_initializer import (
    SystemUserInitializer,
)
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.infrastructure.repositories.message_repository import MessageRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.leo.assistant import Assistant
from app.leo.context.engine import ContextEngine
from app.leo.context.providers.history_provider import (
    HistoryProvider,
)
from app.leo.prompt_builder import PromptBuilder
from app.leo.prompt_loader import PromptLoader


DATABASE_PATH = Path("data/leo.db")
SCHEMA_PATH = Path("app/infrastructure/database/schema.sql")
PROMPTS_PATH = Path("app/leo/prompts")


async def initialize():

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

    system_user_initializer = SystemUserInitializer(
        user_repository,
    )

    await system_user_initializer.initialize()

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

    history_provider = HistoryProvider(
        conversation_store=conversation_store,
    )

    context_engine = ContextEngine(
        loader=prompt_loader,
        history_provider=history_provider,
    )

    prompt_builder = PromptBuilder()

    ai = create_ai_client()

    assistant = Assistant(
        context_engine=context_engine,
        prompt_builder=prompt_builder,
        ai=ai,
    )

    return (
        assistant,
        conversation_store,
    )


def main() -> None:

    assistant, conversation_store = asyncio.run(
        initialize(),
    )

    bot = TelegramBot(
        assistant=assistant,
        conversation_store=conversation_store,
    )

    print("Leo started.")

    bot.run()


if __name__ == "__main__":
    main()
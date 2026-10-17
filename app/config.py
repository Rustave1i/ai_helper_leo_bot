from pathlib import Path
import os

from dotenv import load_dotenv

# ==========================================
# Пути проекта
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# ==========================================
# Memory
# ==========================================
_memory_database_path = Path(
    os.getenv(
        "MEMORY_DATABASE_PATH",
        "data/conversation_memory.sqlite3",
    )
)
MEMORY_DATABASE_PATH = (
    _memory_database_path
    if _memory_database_path.is_absolute()
    else BASE_DIR / _memory_database_path
)

# ==========================================
# AI
# ==========================================

AI_PROVIDER = os.getenv(
    "AI_PROVIDER",
    "openrouter",
)

AI_TIMEOUT = int(
    os.getenv(
        "AI_TIMEOUT",
        "90",
    )
)

AI_RETRIES = int(
    os.getenv(
        "AI_RETRIES",
        "3",
    )
)

AI_RETRY_DELAY = int(
    os.getenv(
        "AI_RETRY_DELAY",
        "2",
    )
)

HTTP_TIMEOUT = int(
    os.getenv(
        "HTTP_TIMEOUT",
        "90",
    )
)

HTTP_RETRIES = int(
    os.getenv(
        "HTTP_RETRIES",
        "3",
    )
)

HTTP_RETRY_DELAY = int(
    os.getenv(
        "HTTP_RETRY_DELAY",
        "2",
    )
)

# ==========================================
# Telegram
# ==========================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


def get_telegram_token() -> str:
    """Возвращает настроенный Telegram token или завершает запуск с понятной ошибкой."""

    token = TELEGRAM_TOKEN

    if token is None or not token.strip():
        raise RuntimeError(
            "Telegram token is not configured. Set TELEGRAM_TOKEN."
        )

    return token

# ==========================================
# Mistral
# ==========================================

MISTRAL_API_KEY = os.getenv(
    "MISTRAL_API_KEY",
)

MISTRAL_MODEL = os.getenv(
    "MISTRAL_MODEL",
    "mistral-small-latest",
)

# ==========================================
# Gemini
# ==========================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)

# ==========================================
# OpenRouter
# ==========================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/auto",
)

# ==========================================
# OpenWeather
# ==========================================

OPENWEATHER_API_KEY = os.getenv(
    "OPENWEATHER_API_KEY",
    "",
)

from pathlib import Path
import os

from dotenv import load_dotenv

# ==========================================
# Пути проекта
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

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

# ==========================================
# Telegram
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

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
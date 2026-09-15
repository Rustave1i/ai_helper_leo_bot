from pathlib import Path
import os

from dotenv import load_dotenv

# Корневая папка проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем .env
load_dotenv(BASE_DIR / ".env")

# ==========================================
# База данных
# ==========================================
DB_PATH = BASE_DIR / "data" / "bot.db"

# Сколько последних сообщений чата использовать как контекст для агента
CONTEXT_MESSAGES = int(os.getenv("CONTEXT_MESSAGES", "100"))

# ==========================================
# Какой AI использовать
# ==========================================
AI_PROVIDER = os.getenv("AI_PROVIDER", "mistral")

# ==========================================
# Telegram
# ==========================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ==========================================
# Mistral
# ==========================================
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = os.getenv(
    "MISTRAL_MODEL",
    "mistral-small-latest",
)

# ==========================================
# Gemini
# ==========================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)

# ==========================================
# OpenRouter (universal gateway: ChatGPT, Claude, Llama и др.)
# ==========================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "free",
)

# ==========================================
# OpenWeather
# ==========================================
OPENWEATHER_API_KEY = os.getenv(
    "OPENWEATHER_API_KEY",
    "",
)

# ==========================================
# Сервисы рейтингов/поиска (для совета с отзывами)
# ==========================================
# Выбор: 2gis | yandex | none (без внешних запросов)
RATING_PROVIDER = os.getenv("RATING_PROVIDER", "none")

# 2ГИС API
GIS_API_KEY = os.getenv("GIS_API_KEY", "")

# Яндекс Карты API
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "")

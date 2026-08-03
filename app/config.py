from pathlib import Path
import os

from dotenv import load_dotenv

# Корневая папка проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем .env
load_dotenv(BASE_DIR / ".env")

# ==========================================
# Какой AI использовать
# ==========================================
AI_PROVIDER = os.getenv("AI_PROVIDER", "mistral")

# ==========================================
# Telegram
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN")

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
# OpenWeather
# ==========================================
OPENWEATHER_API_KEY = os.getenv(
    "OPENWEATHER_API_KEY",
    "",
)
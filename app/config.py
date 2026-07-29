from pathlib import Path
from dotenv import load_dotenv
import os

# Корневая папка проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные из файла .env
load_dotenv(BASE_DIR / ".env")

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Mistral AI
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL = os.getenv("MODEL", "mistral-small-latest")

# OpenWeather
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if __name__ == "__main__":
    print(f"BOT_TOKEN: {BOT_TOKEN[:10]}...")
    print(f"MISTRAL_API_KEY: {MISTRAL_API_KEY[:10]}...")
    print(f"OPENWEATHER_API_KEY: {OPENWEATHER_API_KEY[:10]}...")
    print(f"MODEL: {MODEL}")
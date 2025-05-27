import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
if TELEGRAM_CHANNEL_ID:
    try:
        TELEGRAM_CHANNEL_ID = int(TELEGRAM_CHANNEL_ID)
    except ValueError:
        pass  # оставляем строку-username

PRODAMUS_FORM_URL = os.getenv("PRODAMUS_FORM_URL")
PRODAMUS_SECRET_KEY = os.getenv("PRODAMUS_SECRET_KEY")
DB_PATH = os.getenv("DB_PATH", "database.sqlite")

# Администраторы бота (Telegram IDs)
ADMIN_IDS = [
    int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
]

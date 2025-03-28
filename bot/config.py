import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_URL = os.getenv("CHANNEL_URL")
GROUP_ID = os.getenv("GROUP_ID")
GROUP_URL = os.getenv("GROUP_URL")
Y_KASSA_TOKEN = os.getenv("Y_KASSA_TOKEN")
EXCEL_FILE = os.getenv("EXCEL_FILE")
BOT_USERNAME = os.getenv("BOT_USERNAME", "clients_zhukata_bot")

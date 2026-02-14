import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
XAPI_KEY = os.getenv("XAPI_KEY")

FORCE_CHANNEL = os.getenv("FORCE_CHANNEL")  # without @
ADMIN_ID = int(os.getenv("ADMIN_ID"))

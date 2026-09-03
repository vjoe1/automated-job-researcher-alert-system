import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
API_KEY = os.environ["BOT_SECRET_KEY"]
API_HEADERS = {"X-API-Key": API_KEY}
PAGE_SIZE = 10
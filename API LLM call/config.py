import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise SystemExit("GEMINI_API_KEY not found. Please put it in the .env file.")

MODEL = "gemini-2.5-flash"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
URL = f"{BASE_URL}/{MODEL}:generateContent"

HEADERS = {
    "x-goog-api-key": API_KEY,
    "Content-Type": "application/json",
}

SYSTEM_PROMPT = "You are a helpful assistant. Be concise."

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0 # seconds

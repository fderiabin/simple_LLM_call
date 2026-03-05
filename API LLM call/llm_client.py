import logging
import requests
from config import URL, HEADERS, SYSTEM_PROMPT, CONNECT_TIMEOUT, READ_TIMEOUT, MAX_RETRIES, RETRY_BASE_DELAY
from retry import with_retry

logger = logging.getLogger(__name__)


def send_message(conversation_history: list[dict]) -> str:
    """
    Send the full conversation history to Gemini and return
    the assistant's reply as a string.
    """
    payload = {
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": conversation_history,
    }

    logger.info("Sending request to Gemini (%d turns)...", len(conversation_history))

    def make_request():
        return requests.post(
            URL,
            headers=HEADERS,
            json=payload,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
        )

    try:
        response = with_retry(make_request, max_retries=MAX_RETRIES, base_delay=RETRY_BASE_DELAY)
    except requests.Timeout:
        raise SystemExit("Timed out connecting to Gemini.")
    except requests.RequestException as e:
        raise SystemExit(f"Request failed: {e}")

    logger.info("Received response (status=%s)", response.status_code)

    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]
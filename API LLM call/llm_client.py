import logging
import requests
from config import URL, STREAM_URL, HEADERS, SYSTEM_PROMPT, CONNECT_TIMEOUT, READ_TIMEOUT, MAX_RETRIES, RETRY_BASE_DELAY
from retry import with_retry
import json

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

def send_message_stream(conversation_history: list[dict]) -> str:
    """
    Send the conversation to Gemini and print the response
    word-by-word as it streams in. Returns the full reply.
    """
    payload = {
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": conversation_history,
    }

    logger.info("Sending streaming request to Gemini (%d turns)...", len(conversation_history))

    try:
        response = requests.post(
            STREAM_URL,
            headers=HEADERS,
            json=payload,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            stream=True,  # This is the key difference
        )
    except requests.Timeout:
        raise SystemExit("Timed out connecting to Gemini.")
    except requests.RequestException as e:
        raise SystemExit(f"Request failed: {e}")

    if not response.ok:
        logger.error("Error %s: %s", response.status_code, response.text)
        response.raise_for_status()

    full_reply = []

    for line in response.iter_lines(decode_unicode=True):
        # SSE lines look like: data: {"candidates": [...]}
        if not line or not line.startswith("data: "):
            continue

        raw_json = line[len("data: "):]  # strip the "data: " prefix

        try:
            chunk = json.loads(raw_json)
        except json.JSONDecodeError:
            continue

        # Extract the text piece from this chunk
        parts = chunk.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        for part in parts:
            text = part.get("text", "")
            if text:
                print(text, end="", flush=True)
                full_reply.append(text)

    print()  # newline after the stream finishes
    return "".join(full_reply)
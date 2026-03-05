import time
import logging

logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = {429, 500, 502, 503}

def with_retry(request_func, max_retries = 3, base_delay = 1.0):
    """
    A decorator function that wraps an API call with a retry mechanism for handling failed requests.
    Returns the successful response, or raises SystemExit after exhausting retries."""
    for attempt in range(max_retries + 1):
        response = request_func()
        if response.ok:
            return response
        
        if response.status_code not in RETRYABLE_STATUS_CODES:
            logger.error("Non-retryable error %s: %s", response.status_code, response.text)
            response.raise_for_status()

        if attempt == max_retries:
            logger.error("All %d retries exhausted. Last status: %s", max retries, response.status_code)
            response.raise_for_status()

        delay = base_delay * (2 ** attempt) # 1s, 2s, 4s
        logger.warning("" \
        "Retryable error %s. Waiting %.1fs before retry %d/%d...", 
        response.status_code, delay, attempt + 1, max_retries,
        )
        time.sleep(delay)
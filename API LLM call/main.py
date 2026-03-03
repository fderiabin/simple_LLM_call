import os
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv


#Loading .env from the same folder as this file (adapt if needed):
load_dotenv()

#Assign the variable to a local variable:
API_KEY = os.getenv("GEMINI_API_KEY")

#None has falsy state. So does "". So if we do not find a variable, we send an error.
if not API_KEY:
    raise SystemExit("GEMINI_API_KEY not found. Please put it in the .env file.")

#Set logging variables:
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

#We set up the request:
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

headers = {
    "x-goog-api-key": API_KEY,  # or your API_KEY variable
    "Content-Type": "application/json",
}

payload = {
    "contents": [
        {"role": "user", 
         "parts": [{"text": "Say hello in one short sentence."}]
         }
    ]
}
#API key here: google AI studio, then press API Key
logger.info("Sending request to Gemini...")

#Managing the hanging part:
try:
    response = requests.post(
        URL,
        headers=headers,
        json=payload,
        timeout=(10, 30),  # (connect timeout, read timeout) in seconds
    )
except requests.Timeout:
    raise SystemExit("Timed out connecting to Gemini. Network/DNS/proxy issue likely.")
except requests.RequestException as e:
    raise SystemExit(f"Request failed: {e}")

logger.info("Received response (status=%s)", response.status_code)

if not response.ok:
    logger.error("Error body: %s", response.text)
response.raise_for_status()

data = response.json()
print(data["candidates"][0]["content"]["parts"][0]["text"])

payload_2 = {
    "contents": [
        {"role": "user", 
         "parts": [{"text": f"Last time you said: {data['candidates'][0]['content']['parts'][0]['text']}. Anything else you want to add?"
                    }]
         }
    ]
}

if response.json()["candidates"][0]["content"]["parts"][0]["text"][-1] == "!":
    response_2 = requests.post(
        URL,
        headers=headers,
        json=payload_2,
        timeout=(10, 30),  # (connect timeout, read timeout) in seconds
    )

data_2 = response_2.json()
print(data_2["candidates"][0]["content"]["parts"][0]["text"])
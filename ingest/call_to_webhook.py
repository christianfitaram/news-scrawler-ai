import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Separate credentials for fetching article data and signing webhook calls.
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "eyJAdminK3y-2025!zXt9fGHEMPLq4RsVm7DwuJXeb6u")
WEBHOOK_SIGNATURE = os.getenv("WEBHOOK_SIGNATURE", NEWSAPI_KEY)


def send_to_webhook(insert_id, webhook_url=None):
    try:
        payload = get_news_data(insert_id)
        if not payload:
            print("No data found to send to webhook.")
            return None

        # Basic sanity check to catch malformed payloads before hitting the webhook
        required_fields = ["article_id", "url", "title", "text", "topic", "source", "sentiment", "scraped_at"]
        missing = [f for f in required_fields if payload.get(f) in (None, "")]
        if missing:
            print(f"Payload missing required fields {missing}; aborting webhook call.")
            return None

        # Prepare headers (include signature expected by the webhook)
        headers = {
            "Content-Type": "application/json",
            "X-Signature": WEBHOOK_SIGNATURE,
        }

        target_url = webhook_url or os.getenv("WEBHOOK_URL", "https://servicesemantic.newsapi.one/webhook/news")

        # Log outgoing request for debugging
        try:
            print(f"Sending webhook POST to: {target_url}")
            print(f"Headers: {headers}")
            print("Payload:", json.dumps(payload, ensure_ascii=False))
        except Exception:
            # Fallback if payload is not JSON-serializable
            print("Payload (repr):", repr(payload))

        # Send request with a timeout
        response = requests.post(target_url, json=payload, headers=headers, timeout=30)

        try:
            response.raise_for_status()
            print(f"Webhook POST succeeded: {response.status_code} Body: {response.text}")
            # Attempt to return JSON body if any
            try:
                return response.json()
            except Exception:
                return None
        except requests.HTTPError as http_err:
            # Log response body to see validation errors (422 details)
            print(f"Error sending to webhook: {http_err} Status: {response.status_code} Body: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        # Network-level errors, timeouts, DNS, etc.
        print(f"Error sending to webhook (network): {e}")
        return None


def get_news_data(insert_id, timeout=10):
    base_url = f"https://newsapi.one/v1/news/{insert_id}?apiKey={NEWSAPI_KEY}"
    try:
        response = requests.get(base_url, timeout=timeout)
        response.raise_for_status()
        dataRaw =  response.json()
        data = dataRaw.get("data", {})
        if not data:
            print(f"No news data found for ID: {insert_id}")
            return None
        data_to_return = {
            "article_id": data.get("id"),
            "url": data.get("url"),
            "title": data.get("title"),
            "text": data.get("text"),
            "topic": data.get("topic"),
            "source": data.get("source"),
            "sentiment": data.get("sentiment"),
            "scraped_at": data.get("scraped_at"),
        }
        print(data_to_return)
        # Log fetched data summary for debugging
        try:
            print(f"Fetched news data for {insert_id}:", json.dumps(data_to_return, ensure_ascii=False))
        except Exception:
            print(f"Fetched news data for {insert_id} (repr):", repr(data_to_return))
        return data_to_return
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news data: {e}")
        return None

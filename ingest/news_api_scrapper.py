import os

import requests
from datetime import timezone, datetime, UTC, date
from ingest.utils import is_urls_processed_already, fetch_and_extract
from lib.repositories.link_pool_repository import LinkPoolRepository

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

repo = LinkPoolRepository()
# Your combined OR query for topics
TOPIC_QUERY = (
    "politics OR government OR science OR research OR "
    "technology OR innovation OR health OR medicine OR business OR finance OR "
    "OR crime OR justice OR climate OR environment OR "
    "education OR war OR conflict"
)

UNWANTED_CONTENT_SNIPPET = "A required part of this site"


def _sample_date() -> date:
    return datetime.now(UTC).date()


def scrape_newsapi_stream(language='en', page_size=50):
    base_url = "https://newsapi.org/v2/everything"

    # We'll fetch two pages to get approx 200 articles
    for page in [1, 2]:
        try:
            response = requests.get(
                base_url,
                params={
                    "q": TOPIC_QUERY,
                    "language": language,
                    "from": _sample_date(),
                    "to": _sample_date(),
                    "sortBy": "publishedAt",
                    "pageSize": page_size,
                    "page": page,
                    "apiKey": NEWSAPI_KEY
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Error fetching news (page {page}): {e}")
            return  # Stops the generator if request fails

        for article in data.get("articles", []):
            # Exclude unwanted content
            content = article.get("content") or ""
            if UNWANTED_CONTENT_SNIPPET in content:
                continue

            url = article.get("url")
            if not url:
                continue
            if is_urls_processed_already(url):
                continue

            full_text = fetch_and_extract(url)
            if full_text is None or not full_text.strip():
                continue  # Skip this article if no content was extracted

            repo.insert_link({"url": url})

            yield {
                "title": article.get("title", "").strip(),
                "text": full_text.strip(),
                "url": url,
                "source": article.get("source", {}).get("name", ""),
                "scraped_at": datetime.now(timezone.utc),
            }


def scrape_all_categories(language='en', page_size=100, pages_per_category=1, target_date=None):
    if target_date is None:
        target_date = datetime.now(UTC).date()  # timezone-aware UTC date
        # target_date = date(2025, 8, 9)

    categories = [
        "business",
        "general",
        "health",
        "science",
        "technology",
    ]

    for category in categories:
        for page in range(1, pages_per_category + 1):
            try:
                response = requests.get(
                    "https://newsapi.org/v2/top-headlines",
                    params={
                        "apiKey": NEWSAPI_KEY,
                        "language": language,
                        "category": category,
                        "pageSize": page_size,
                        "page": page,
                    },
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                print(f"Error fetching category '{category}', page {page}: {e}")
                continue

            for article in data.get("articles", []):
                published_at_str = article.get("publishedAt")
                if not published_at_str:
                    continue

                try:
                    published_at = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%SZ").date()
                except ValueError:
                    print(f"❌ Invalid publishedAt format: {published_at_str}")
                    continue

                if published_at != target_date:
                    print(f"Skipping article from {published_at_str} (wanted {target_date})")
                    continue
                content = article.get("content") or ""
                if "A required part of this site couldnt load" in content:
                    continue

                url = article.get("url")
                if not url or is_urls_processed_already(url):
                    continue

                full_text = fetch_and_extract(url)
                if not full_text or not full_text.strip():
                    continue

                repo.insert_link({"url": url})

                yield {
                    "title": article.get("title", "").strip(),
                    "text": full_text.strip(),
                    "url": url,
                    "source": article.get("source", {}).get("name", ""),
                    "scraped_at": datetime.now(timezone.utc),
                    "published_at": published_at_str,
                    "category": category
                }

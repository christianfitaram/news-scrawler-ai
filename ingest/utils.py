import trafilatura
from lib.repositories.link_pool_repository import LinkPoolRepository

repo = LinkPoolRepository()


def is_urls_processed_already(url):
    is_it = repo.is_link_successfully_processed(url)
    if is_it:
        print(f"{url} it has been processed already. Skipping ")
        return True
    else:
        return False


# Method for extract the article data
def fetch_and_extract(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            return trafilatura.extract(downloaded)
    except Exception as e:
        print(f"Failed to fetch content from {url}: {e}")
    return None

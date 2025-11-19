from datetime import datetime, date, UTC, timezone
from lib.repositories.articles_repository import ArticlesRepository
from lib.repositories.metadata_repository import MetadataRepository
from lib.repositories.link_pool_repository import LinkPoolRepository

def _sample_date():
    dateNow = datetime.now(UTC).date()
    print(dateNow)


def articles():
    repo_articles = ArticlesRepository()
    articles = repo_articles.get_articles({})
    for article in articles:
        print(article)
        print("----")


def access_metadata():
    repo_metadat = MetadataRepository()
    docs = repo_metadat.get_metadata({"_id": "1-2025-09-17"})
    for doc in docs:
        print(doc)
        print("----")
def delete_metadata():
    repo_metadat = MetadataRepository()
    result = repo_metadat.delete_metadata_one({"_id": "1-2025-09-17"})
    print(f"Deleted {result} documents.")

def get_links():
    repo = LinkPoolRepository()
    links = repo.get_link({})
    for link in links:
        print(link)
        print("----")

def getAllArticlesAndEdit():
    repo = ArticlesRepository()
    articles = repo.get_articles({})
    for article in articles:
        print(article)
        print("----")
        repo.update_articles({"_id": article["_id"]}, {"$set": {"relevanceStatus": "pending"}})
        print(f"Updated article {article['_id']} to set relevanceStatus to pending")

def countArticles():
    repo = ArticlesRepository()
    count = repo.count_articles({})
    print(f"Total articles count: {count}")

if __name__ == "__main__":
    countArticles()

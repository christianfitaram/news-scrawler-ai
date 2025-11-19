# lib/repositories/clean_articles_repository.py
from typing import Any, Dict, Iterable, List, Optional, Tuple
from lib.db.mongo_client import get_db
from pymongo.collection import Collection


class CleanArticlesRepository:
    def __init__(self) -> None:
        self.collection: Collection = get_db()["clean_articles"]

    def create_articles(self, article_data: Dict[str, Any]) -> str:
        result = self.collection.insert_one(article_data)
        return str(result.inserted_id)

    def get_articles(self, params: Dict[str, Any]):
        return self.collection.find(params)

    def get_articles_broad(self, filter_param: Dict[str, Any], projection_param: Optional[Dict[str, int]] = None):
        return self.collection.find(filter_param, projection=projection_param)

    def get_one_article(self, params: Dict[str, Any], sorting: Optional[List[Tuple[str, int]]] = None):
        return self.collection.find_one(params, sort=sorting) if sorting else self.collection.find_one(params)

    def update_articles(self, selector: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        result = self.collection.update_one(selector, update_data)
        return result.modified_count

    def delete_articles(self, selector: Dict[str, Any]) -> int:
        result = self.collection.delete_many(selector)
        return result.deleted_count

    def count_articles(self, params: Dict[str, Any]) -> int:
        return self.collection.count_documents(params)

    def setup_indexes(self) -> None:
        name = self.collection.create_index([("isCleaned", 1), ("sample", 1)])
        print(f"✅ Compound index '{name}' created on 'isCleaned + sample'")

    def create_index(self, keys: List[Tuple[str, int]], **kwargs) -> str:
        """
        Create an index on the clean_articles collection.
        :param keys: List of tuples specifying the fields and their sort order.
        :param kwargs: Additional options for index creation.
        :return: The name of the created index.
        """
        return self.collection.create_index(keys, **kwargs)

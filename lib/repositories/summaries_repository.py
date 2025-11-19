# lib/repositories/summaries_repository.py
from typing import Any, Dict, Iterable, List, Optional, Tuple
from lib.db.mongo_client import get_db
from pymongo.collection import Collection


class SummariesRepository:
    def __init__(self) -> None:
        self.collection: Collection = get_db()["summaries"]

    def create_articles(self, data: Dict[str, Any]) -> str:
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def get_articles(self, params: Dict[str, Any], projection: Optional[Dict[str, int]] = None):
        return self.collection.find(params, projection) if projection else self.collection.find(params)

    def get_distinct_samples(self, sample_str: str) -> List[str]:
        # case-insensitive suffix match for -YYYY-MM-DD
        regex_filter = {"sample": {"$regex": sample_str, "$options": "i"}}
        return list(self.collection.distinct("sample", regex_filter))

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

# lib/repositories/trend_threads_repository.py
from typing import Dict, Any, Iterable, List, Tuple
from lib.db.mongo_client import get_db
from pymongo.collection import Collection


class TrendThreadsRepository:

    def __init__(self) -> None:
        self.collection: Collection = get_db()["summaries"]

    def get_threads_on(self, date_iso: str) -> Iterable[Dict[str, Any]]:
        return self.collection.find({"date": date_iso})

    def get_recent_for_thread(self, thread_id: str, since_iso: str) -> Iterable[Dict[str, Any]]:
        return self.collection.find({"thread_id": thread_id, "date": {"$gte": since_iso}}).sort("date", 1)

    def upsert_today(self, selector: Dict[str, Any], doc: Dict[str, Any]) -> None:
        self.collection.update_one(selector, {"$set": doc}, upsert=True)

    def create_index(self, keys: List[Tuple[str, int]], **kwargs) -> str:
        """
        Create an index on the summaries collection.
        :param keys: List of tuples specifying the fields and their sort order.
        :param kwargs: Additional options for index creation.
        :return: The name of the created index.
        """
        return self.collection.create_index(keys, **kwargs)

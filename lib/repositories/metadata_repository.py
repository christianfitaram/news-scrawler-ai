# lib/repositories/metadata_repository.py
from typing import Any, Dict, Iterable, List, Optional, Tuple
from lib.db.mongo_client import get_db
from pymongo.collection import Collection


class MetadataRepository:
    def __init__(self) -> None:
        self.collection: Collection = get_db()["metadata"]

    def insert_metadata(self, data: Dict[str, Any]) -> str:
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def get_metadata(self, param: Dict[str, Any], sorting: Optional[List[Tuple[str, int]]] = None):
        return self.collection.find(param, sort=sorting) if sorting else self.collection.find(param)

    def get_one_metadata(self, param: Dict[str, Any], sorting: Optional[List[Tuple[str, int]]] = None):
        return self.collection.find_one(param, sort=sorting) if sorting else self.collection.find_one(param)

    def get_metadata_broad(self, filter_param: Dict[str, Any], projection_param: Optional[Dict[str, int]] = None):
        return self.collection.find(filter_param, projection=projection_param)

    def setup_indexes(self) -> None:
        name = self.collection.create_index("is_articles_processed")
        print(f"✅ Index '{name}' created successfully on 'is_articles_processed'")

    def create_index(self, keys: List[Tuple[str, int]], **kwargs) -> str:
        """
        Create an index on the metadata collection.
        :param keys: List of tuples specifying the fields and their sort order.
        :param kwargs: Additional options for index creation.
        :return: The name of the created index.
        """
        return self.collection.create_index(keys, **kwargs)

    def update_metadata(self, selector: Dict[str, Any], update_data: Dict[str, Any]):
        return self.collection.update_one(selector, update_data)

    def update_metadata_upsert(self, selector: Dict[str, Any], update_data: Dict[str, Any]):
        return self.collection.update_one(selector, update_data, upsert=True)

    def delete_metadata_many(self, selector: Dict[str, Any]) -> int:
        result = self.collection.delete_many(selector)
        return result.deleted_count

    def delete_metadata_one(self, selector: Dict[str, Any]) -> int:
        # FIX: your original used delete_many here—switched to delete_one.
        result = self.collection.delete_one(selector)
        return result.deleted_count

    def count_all_documents(self) -> int:
        return self.collection.count_documents({})

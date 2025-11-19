# lib/repositories/link_pool_repository.py
from typing import Any, Dict, Optional, List, Tuple
from lib.db.mongo_client import get_db
from pymongo.collection import Collection
from pymongo import ReturnDocument


class LinkPoolRepository:
    def __init__(self) -> None:
        self.collection: Collection = get_db()["link_pool"]

    # --- Creation / Upsert ---
    def insert_link(self, data: Dict[str, Any]) -> str:
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def update_link_in_pool(
            self,
            selector: Dict[str, Any],
            update_data: Dict[str, Any],
            *,
            upsert: bool = False,
    ) -> int:
        """Return modified_count; when upsert=True, record may be inserted."""
        result = self.collection.update_one(selector, update_data, upsert=upsert)
        return result.modified_count

    def upsert_link(self, url: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Ensure a link doc exists; returns the whole doc after upsert."""
        extra = extra or {}
        doc = self.collection.find_one_and_update(
            {"url": url},
            {"$setOnInsert": {"url": url}, "$set": extra},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return doc

    # --- Queries ---
    def get_link(self, params: Dict[str, Any]):
        """Returns a cursor (plural). Consider renaming to find_links()."""
        return self.collection.find(params)

    def find_link(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Single document or None."""
        return self.collection.find_one(params)

    def find_one_by_url(self, url: str, *, projection: Optional[Dict[str, int]] = None) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"url": url}, projection=projection)

    # --- Convenience gates for the use-case ---
    def ensure_tracked(self, url: str) -> Dict[str, Any]:
        """Idempotent: creates {url} if not present; returns the doc."""
        return self.upsert_link(url)

    def is_link_successfully_processed(self, url: str) -> bool:
        """Kept for backward compatibility."""
        doc = self.collection.find_one({"url": url}, projection={"is_articles_processed": 1, "in_sample": 1})
        return bool(doc and (doc.get("is_articles_processed") or doc.get("in_sample")))

    def is_processed(self, url: str) -> bool:
        """Preferred name going forward."""
        return self.is_link_successfully_processed(url)

    def mark_processed(self, url: str, sample_id: str) -> int:
        """Idempotently mark a link as processed and attach sample."""
        res = self.collection.update_one(
            {"url": url},
            {"$set": {"is_articles_processed": True, "in_sample": sample_id}},
            upsert=True,
        )
        return res.modified_count

    # --- Admin / maintenance ---
    def setup_indexes(self) -> None:
        # Unique URL to avoid duplicates
        name_url = self.collection.create_index("url", unique=True)
        name_proc = self.collection.create_index("is_articles_processed")
        print(f"✅ Indexes created: {name_url} (unique on url), {name_proc} (processed flag)")

    def create_index(self, keys: List[Tuple[str, int]], **kwargs) -> str:
        """
        Create an index on the link_pool collection.
        :param keys: Dictionary specifying the fields and their sort order.
        :param kwargs: Additional options for index creation.
        :return: The name of the created index.
        """
        return self.collection.create_index(keys, **kwargs)

    def delete_link(self, selector: Dict[str, Any]) -> int:
        result = self.collection.delete_one(selector)
        return result.deleted_count

    def delete_links(self, selector: Dict[str, Any]) -> int:
        result = self.collection.delete_many(selector)
        return result.deleted_count

    def count(self, params: Dict[str, Any]) -> int:
        return self.collection.count_documents(params)

# lib/db/mongo_client.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

_client = None
_db = None

# 1) Load .env automatically (once, on import)
#    find_dotenv() searches upward until it finds a .env; returns "" if not found.
_env_path = find_dotenv()
load_dotenv(_env_path, override=False)


load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")  # project root


def _require_env(name: str) -> str:
    """Get an env var or raise a clear error if missing/empty."""
    value = os.getenv(name, "").strip()
    if not value:
        where = _env_path if _env_path else "(no .env found)"
        raise RuntimeError(
            f"Environment variable '{name}' is not set or empty. "
            f"Loaded .env from: {where}. "
            f"Make sure '{name}' is defined there or in your shell."
        )
    return value


def get_client() -> MongoClient:
    global _client
    if _client is None:
        uri = _require_env("MONGO_URI")
        appname = os.getenv("APP_NAME", "trend-app")
        # Optional: a couple of sane defaults
        _client = MongoClient(
            uri,
            appname=appname,
            serverSelectionTimeoutMS=8000,  # fail faster if unreachable
        )
    return _client


def get_db():
    global _db
    if _db is None:
        db_name = _require_env("MONGODB_DB")
        _db = get_client()[db_name]
    return _db

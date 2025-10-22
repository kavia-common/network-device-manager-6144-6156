"""MongoDB connection utilities using pymongo.

Provides a singleton MongoClient and helper to access the devices collection.
Reads MONGODB_URI and MONGODB_DB from Flask app config.
"""

from typing import Optional
from pymongo import MongoClient
from flask import current_app

_client: Optional[MongoClient] = None

def _get_uri_and_db():
    """Fetch MongoDB config from Flask app config. Raise clear errors if missing."""
    uri = current_app.config.get("MONGODB_URI")
    dbname = current_app.config.get("MONGODB_DB")
    missing = []
    if not uri:
        missing.append("MONGODB_URI")
    if not dbname:
        missing.append("MONGODB_DB")
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
    return uri, dbname

# PUBLIC_INTERFACE
def get_client() -> MongoClient:
    """Return a singleton MongoClient instance configured from app config."""
    global _client
    if _client is None:
        uri, _ = _get_uri_and_db()
        _client = MongoClient(uri)
    return _client

# PUBLIC_INTERFACE
def get_db():
    """Return the MongoDB database object based on app config."""
    client = get_client()
    _, dbname = _get_uri_and_db()
    return client[dbname]

# PUBLIC_INTERFACE
def get_devices_collection():
    """Return the devices collection from the configured database."""
    db = get_db()
    return db["devices"]

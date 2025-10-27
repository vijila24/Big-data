from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from .config import MONGODB_URI, MONGODB_DB

_client = MongoClient(MONGODB_URI)
_db = _client[MONGODB_DB]

reviews = _db["reviews"]
products = _db["products"]

def ensure_indexes():
    reviews.create_index([("product_id", ASCENDING), ("created_at", DESCENDING)])
    reviews.create_index([("nlp.sentiment.label", ASCENDING), ("created_at", DESCENDING)])
    reviews.create_index([("nlp.sdg12_signals.label", ASCENDING)])
    reviews.create_index([("source.platform", ASCENDING)])
    reviews.create_index([("text", TEXT)])

    products.create_index([("sku", ASCENDING)], unique=True)
    products.create_index([("brand", ASCENDING), ("category", ASCENDING)])

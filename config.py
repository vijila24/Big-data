import os

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "sdg12_reviews")
SENTIMENT_MODEL = os.getenv("SENTIMENT_MODEL", "vader")
PIPELINE_VERSION = "0.1.0"

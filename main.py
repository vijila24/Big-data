from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, Body, Query
from pydantic import BaseModel

from .db import reviews, ensure_indexes
from .pipeline import process_review

app = FastAPI(title="SDG12 Review Sentiment API", version="0.1.0")


class ReviewIn(BaseModel):
    product_id: str
    product_ref: Optional[dict] = None
    source: Optional[dict] = None
    text: str
    rating: Optional[float] = None
    created_at: Optional[datetime] = None
    meta: Optional[dict] = None


@app.on_event("startup")
def on_start():
    ensure_indexes()


@app.post("/ingest/reviews")
def ingest_reviews(items: List[ReviewIn] = Body(...)):
    docs = []
    for item in items:
        base = item.model_dump()
        base.setdefault("created_at", datetime.utcnow())
        base.setdefault("source", {})
        doc = process_review(base)
        docs.append(doc)
    if docs:
        reviews.insert_many(docs)
    return {"inserted": len(docs)}


@app.get("/analytics/sentiment-overview")
def sentiment_overview(
    product_id: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    days: int = Query(90, ge=1, le=365),
):
    since = datetime.utcnow() - timedelta(days=days)
    match = {"created_at": {"$gte": since}}
    if product_id:
        match["product_id"] = product_id
    if brand:
        match["product_ref.brand"] = brand
    if category:
        match["product_ref.category"] = category

    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": None,
            "avg_sentiment": {"$avg": "$nlp.sentiment.score"},
            "n": {"$sum": 1}
        }},
    ]
    agg = list(reviews.aggregate(pipeline))
    if not agg:
        return {"avg_sentiment": None, "count": 0}
    return {"avg_sentiment": agg[0]["avg_sentiment"], "count": agg[0]["n"]}


@app.get("/analytics/sdg12-signals")
def sdg12_signals(
    label: Optional[str] = Query(None),
    days: int = Query(90, ge=1, le=365),
):
    since = datetime.utcnow() - timedelta(days=days)
    match = {"created_at": {"$gte": since}}
    pipeline = [
        {"$match": match},
        {"$unwind": "$nlp.sdg12_signals"},
        {"$group": {"_id": "$nlp.sdg12_signals.label", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    results = list(reviews.aggregate(pipeline))
    if label:
        results = [r for r in results if r["_id"] == label]
    return {"signals": results}


@app.get("/analytics/trends")
def trends(days: int = Query(30, ge=1, le=365)):
    since = datetime.utcnow() - timedelta(days=days)
    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
            "avg_sentiment": {"$avg": "$nlp.sentiment.score"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    results = list(reviews.aggregate(pipeline))
    return {"days": results}

# Product Review Sentiment Storage (SDG 12) — Python Package

A minimal FastAPI + MongoDB package to ingest product reviews, run sentiment analysis (VADER) and SDG 12 signal tagging (keywords), and expose analytics endpoints.

## Features

- Ingest reviews via API (batch)
- NLP pipeline: clean, language detect, sentiment (VADER), SDG12 keyword tagging
- MongoDB storage with basic indexes
- Analytics endpoints: sentiment overview, SDG12 signal counts, trends

## Tech stack

- Python 3.10+
- FastAPI, Uvicorn
- MongoDB (local or Atlas)
- pymongo, python-dotenv (optional), vaderSentiment, langdetect, pydantic

## Requirements

- Python 3.10+
- MongoDB running locally (default) or a MongoDB Atlas URI

## Installation

```bash
pip install fastapi uvicorn pymongo python-dotenv vaderSentiment langdetect pydantic
```

## Environment variables (optional)

- `MONGODB_URI` (default: `mongodb://localhost:27017`)
- `MONGODB_DB` (default: `sdg12_reviews`)
- `SENTIMENT_MODEL` (default: `vader`)

You can set these in your shell before running, e.g. on Windows PowerShell:
```powershell
$env:MONGODB_URI = "mongodb://localhost:27017"
$env:MONGODB_DB = "sdg12_reviews"
```

## Run the API

- Using package export from `__init__.py`:
  ```bash
  uvicorn python:app --reload
  ```
- Or via module path:
  ```bash
  uvicorn python.main:app --reload
  ```

Open Swagger UI: http://127.0.0.1:8000/docs

## Endpoints

- POST `/ingest/reviews`
  - Body: JSON array of review objects
  - Example item:
    ```json
    {
      "product_id": "p_001",
      "product_ref": {"brand": "EcoBrand", "category": "Home"},
      "source": {"platform": "web", "country": "IN", "language": "en"},
      "text": "Great bottle, but too much plastic in the packaging.",
      "rating": 4
    }
    ```

- GET `/analytics/sentiment-overview`
  - Query params: `product_id`, `brand`, `category`, `days`

- GET `/analytics/sdg12-signals`
  - Query params: `label`, `days`

- GET `/analytics/trends`
  - Query params: `days`

## Project structure

```
python/
  __init__.py          # exposes FastAPI app (uvicorn python:app)
  config.py            # env config (defaults)
  db.py                # MongoDB connection + indexes
  pipeline.py          # cleaning, language detect, VADER sentiment, SDG12 tagging
  sdg12_taxonomy.py    # SDG12 keyword lists
  main.py              # FastAPI endpoints
```

## Notes

- Ensure MongoDB is reachable via `MONGODB_URI`.
- VADER is fast but simple; swap to a transformer model for higher accuracy if needed.

## Git quickstart

```bash
git init
git add .
git commit -m "Init SDG12 review sentiment python package"
# create repo on GitHub then:
# git remote add origin <your-repo-url>
# git push -u origin main
```

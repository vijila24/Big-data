from typing import Dict, List, Any
from hashlib import md5
from langdetect import detect, LangDetectException
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .sdg12_taxonomy import SDG12_KEYWORDS
from .config import PIPELINE_VERSION

_analyzer = SentimentIntensityAnalyzer()


def clean_text(text: str) -> str:
    return " ".join(text.strip().split())


def detect_language(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def sentiment(text: str) -> Dict[str, Any]:
    scores = _analyzer.polarity_scores(text)
    compound = scores.get("compound", 0.0)
    label = "positive" if compound >= 0.05 else ("negative" if compound <= -0.05 else "neutral")
    return {
        "score": compound,
        "label": label,
        "model": "vader",
        "version": "3.3.2",
    }


def tag_sdg12(text: str) -> List[Dict[str, Any]]:
    text_lc = text.lower()
    tags: List[Dict[str, Any]] = []
    for label, kws in SDG12_KEYWORDS.items():
        matched = [kw for kw in kws if kw.lower() in text_lc]
        if matched:
            score = min(1.0, sum(len(m) for m in matched) / 30.0)
            tags.append({
                "label": label,
                "score": round(score, 3),
                "method": "keywords",
                "keywords_matched": matched,
            })
    return tags


def dedupe_hash(doc: Dict[str, Any]) -> str:
    basis = f"{doc.get('product_id','')}|{doc.get('text','')}|{doc.get('rating','')}"
    return md5(basis.encode("utf-8")).hexdigest()


def process_review(raw: Dict[str, Any]) -> Dict[str, Any]:
    text = clean_text(raw.get("text", ""))
    lang = detect_language(text) if text else "unknown"
    sent = sentiment(text)
    sdg = tag_sdg12(text)

    out = {
        **raw,
        "text": text,
        "nlp": {
            "language": lang,
            "sentiment": sent,
            "sdg12_signals": sdg,
            "aspects": [],
        },
        "meta": {
            **raw.get("meta", {}),
            "pipeline_version": PIPELINE_VERSION,
        }
    }
    out.setdefault("meta", {})
    out["meta"]["dedupe_hash"] = dedupe_hash(out)
    return out

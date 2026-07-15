"""
Sentiment Analysis API
VADER sentiment analysis. Offline, free.
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

router = APIRouter()

@router.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}

analyzer = SentimentIntensityAnalyzer()

class SentimentResult(BaseModel):
    text: str
    sentiment: str
    compound: float
    positive: float
    negative: float
    neutral: float

@router.get("/")
async def root():
    return {"service": "Sentiment Analysis API", "version": "1.1.0", "related": ["Language Detector API"]}

@router.get("/analyze", response_model=SentimentResult)
async def analyze(text: str = Query(..., description="Text to analyze")):
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        sentiment = "positive"
    elif compound <= -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return SentimentResult(
        text=text[:200], sentiment=sentiment, compound=round(compound, 4),
        positive=round(scores["pos"], 4), negative=round(scores["neg"], 4),
        neutral=round(scores["neu"], 4)
    )

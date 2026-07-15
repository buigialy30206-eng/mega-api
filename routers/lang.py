"""
Language Detector API
Detect language from text. 55+ languages supported.
Uses Google's language-detection library. Offline, free.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from langdetect import detect, detect_langs

router = APIRouter()

LANG_NAMES = {
    "en": "English", "zh-cn": "Chinese (Simplified)", "zh-tw": "Chinese (Traditional)",
    "fr": "French", "de": "German", "es": "Spanish", "it": "Italian",
    "pt": "Portuguese", "ru": "Russian", "ja": "Japanese", "ko": "Korean",
    "ar": "Arabic", "hi": "Hindi", "nl": "Dutch", "sv": "Swedish",
    "no": "Norwegian", "da": "Danish", "fi": "Finnish", "pl": "Polish",
    "tr": "Turkish", "vi": "Vietnamese", "th": "Thai", "id": "Indonesian",
    "ms": "Malay", "he": "Hebrew", "uk": "Ukrainian", "ro": "Romanian",
    "bg": "Bulgarian", "cs": "Czech", "el": "Greek", "hu": "Hungarian",
    "sk": "Slovak", "sl": "Slovenian", "lt": "Lithuanian", "lv": "Latvian",
    "et": "Estonian", "hr": "Croatian", "sr": "Serbian", "fa": "Persian",
    "ca": "Catalan", "tl": "Filipino", "bn": "Bengali", "ta": "Tamil",
    "ur": "Urdu", "mr": "Marathi", "te": "Telugu", "gu": "Gujarati",
    "kn": "Kannada", "ml": "Malayalam", "sw": "Swahili", "af": "Afrikaans",
    "sq": "Albanian", "cy": "Welsh", "mk": "Macedonian", "is": "Icelandic",
}

class DetectResult(BaseModel):
    text: str
    language: str
    language_name: str
    confidence: float

@router.api_route("/health", methods=["GET", "HEAD"])
async def health(): return {"status": "ok"}

@router.get("/")
async def root(): return {"service": "Language Detector API", "version": "1.0.0", "related": ["Sentiment Analysis API"]}

@router.get("/detect", response_model=DetectResult)
async def detect_language(text: str = Query(..., description="Text to detect language of")):
    if len(text) < 10:
        return DetectResult(text=text, language="unknown", language_name="Unknown (text too short)", confidence=0.0)

    lang = detect(text)
    probs = detect_langs(text)
    conf = 0.0
    for p in probs:
        if p.lang == lang:
            conf = round(p.prob, 2)
            break

    return DetectResult(
        text=text[:200],
        language=lang,
        language_name=LANG_NAMES.get(lang, lang),
        confidence=conf,
    )

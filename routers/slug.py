"""
Text to Slug API
Convert text to URL-friendly slugs. Pure Python, zero deps.
"""

import re, unicodedata

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

@router.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}

class SlugResult(BaseModel):
    original: str
    slug: str
    length: int

def text_to_slug(text: str, separator: str = "-") -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[-\s]+", separator, text)
    return text

@router.get("/")
async def root():
    return {"service": "Text to Slug API", "version": "1.0.0", "related": ["Markdown to HTML API", "URL Metadata Extractor API"]}

@router.get("/slugify", response_model=SlugResult)
async def slugify(
    text: str = Query(..., description="Text to convert to slug"),
    separator: str = Query("-", description="Word separator, default '-'"),
):
    slug = text_to_slug(text, separator)
    return SlugResult(original=text, slug=slug, length=len(slug))

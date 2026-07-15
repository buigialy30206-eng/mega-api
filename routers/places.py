"""
Places Search API — global business search via OpenStreetMap Overpass API.
Uses system curl for HTTP (bypasses Python proxy issues).
FREE. No API keys. Deploy on Render → RapidAPI → earn USD.
"""

import hashlib
import json
import subprocess
import time
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

router = APIRouter()

@router.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}

OVERPASS = "https://overpass-api.de/api/interpreter"
_cache: dict = {}
CACHE_TTL = 3600

# User query → OSM tag
TAG_MAP = {
    "restaurant": ("amenity", "restaurant"), "cafe": ("amenity", "cafe"),
    "coffee": ("amenity", "cafe"), "coffee shop": ("amenity", "cafe"),
    "bar": ("amenity", "bar"), "pub": ("amenity", "pub"),
    "fast food": ("amenity", "fast_food"), "bakery": ("shop", "bakery"),
    "supermarket": ("shop", "supermarket"), "grocery": ("shop", "supermarket"),
    "pharmacy": ("amenity", "pharmacy"), "bank": ("amenity", "bank"),
    "atm": ("amenity", "atm"), "hotel": ("tourism", "hotel"),
    "motel": ("tourism", "motel"), "hospital": ("amenity", "hospital"),
    "clinic": ("amenity", "clinic"), "dentist": ("amenity", "dentist"),
    "doctor": ("amenity", "doctors"), "veterinary": ("amenity", "veterinary"),
    "vet": ("amenity", "veterinary"), "gas station": ("amenity", "fuel"),
    "plumber": ("craft", "plumber"), "electrician": ("craft", "electrician"),
    "locksmith": ("craft", "locksmith"), "gym": ("leisure", "fitness_centre"),
    "cinema": ("amenity", "cinema"), "museum": ("tourism", "museum"),
    "school": ("amenity", "school"), "university": ("amenity", "university"),
    "library": ("amenity", "library"), "post office": ("amenity", "post_office"),
    "police": ("amenity", "police"), "lawyer": ("office", "lawyer"),
    "hair salon": ("shop", "hairdresser"), "hairdresser": ("shop", "hairdresser"),
    "spa": ("leisure", "spa"), "clothing": ("shop", "clothes"),
    "electronics": ("shop", "electronics"), "hardware": ("shop", "hardware"),
    "car repair": ("shop", "car_repair"),
}

def resolve_tag(query: str) -> tuple[str, str]:
    q = query.lower().strip()
    if q in TAG_MAP:
        return TAG_MAP[q]
    for key, tag in TAG_MAP.items():
        if key in q or q in key:
            return tag
    return ("amenity", q.replace(" ", "_"))

def overpass_query(overpass_ql: str) -> dict:
    """Run an Overpass QL query via curl. Returns parsed JSON."""
    proc = subprocess.run(
        ["curl", "-s", "--connect-timeout", "10", "--max-time", "18",
         "-X", "POST", OVERPASS,
         "-H", "Accept: application/json",
         "-H", "Content-Type: application/x-www-form-urlencoded",
         "--data", overpass_ql],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"curl failed: {proc.stderr[:200]}")
    if not proc.stdout.strip():
        raise RuntimeError("empty response")
    return json.loads(proc.stdout)

class Business(BaseModel):
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    category: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class SearchResponse(BaseModel):
    query: str
    location: str
    total_results: int
    results: list[Business]

def geocode(name: str) -> tuple[float, float, str]:
    """Geocode a place name via Overpass. Prefers more populous places."""
    # Try exact city match first (sorts by population implicitly via OSM order)
    ql = (
        f'[out:json][timeout:10];'
        f'(node["place"="city"]["name"="{name}"];'
        f'node["place"="town"]["name"="{name}"];'
        f'node["place"="village"]["name"="{name}"];'
        f');out center 5;'
    )
    data = overpass_query(ql)
    elements = data.get("elements", [])

    # Pick the one with highest population or most tags
    best = None
    best_score = -1
    for e in elements:
        tags = e.get("tags", {})
        pop = int(tags.get("population", 0))
        is_city = tags.get("place") == "city"
        score = pop + (100000 if is_city else 0)
        if score > best_score:
            best_score = score
            best = e

    if not best:
        raise ValueError(f"Location not found: {name}")

    lat = best.get("lat") or best.get("center", {}).get("lat")
    lng = best.get("lon") or best.get("center", {}).get("lon")
    display = best.get("tags", {}).get("name", name)
    return lat, lng, display

def search_businesses(key: str, val: str, lat: float, lng: float, limit: int) -> list[dict]:
    """Search businesses near coordinates."""
    ql = (
        f'[out:json][timeout:15];'
        f'node["{key}"="{val}"](around:8000,{lat},{lng});'
        f'out body {min(limit * 3, 50)};'
    )
    data = overpass_query(ql)

    results = []
    seen = set()
    for elem in data.get("elements", []):
        t = elem.get("tags", {})
        name = t.get("name", "")
        if not name or name in seen:
            continue
        seen.add(name)

        phone = t.get("phone") or t.get("contact:phone") or t.get("contact:mobile")
        addr_parts = [t.get(k) for k in ["addr:street", "addr:housenumber", "addr:city", "addr:postcode", "addr:state"] if t.get(k)]
        addr = ", ".join(addr_parts) if addr_parts else None

        results.append({
            "name": name, "phone": phone, "address": addr,
            "website": t.get("website") or t.get("contact:website"),
            "category": val, "lat": elem.get("lat"), "lng": elem.get("lon"),
            "rating": None, "review_count": None,
        })
        if len(results) >= limit:
            break
    return results

@router.get("/")
async def root():
    return {
        "name": "Places Search API", "related": ["Company Info API", "IP Geolocation API", "Phone Number Lookup API"],
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "/search": "GET ?query=cafe&location=New+York&limit=10",
            "/search-nearby": "GET ?query=restaurant&lat=40.7128&lng=-74.006&limit=10",
            "/health": "GET health check",
        }
    }

@router.get("/search", response_model=SearchResponse)
async def search(
    query: str = Query(..., description="Business type: cafe, restaurant, hotel, plumber..."),
    location: str = Query(..., description="City/place: New York, London, Tokyo..."),
    limit: int = Query(10, ge=1, le=20),
):
    ck = hashlib.md5(f"{query}|{location}|{limit}".encode()).hexdigest()
    if ck in _cache and time.time() - _cache[ck]["ts"] < CACHE_TTL:
        return _cache[ck]["data"]

    try:
        key, val = resolve_tag(query)
        lat, lng, display = geocode(location)
        raw = search_businesses(key, val, lat, lng, limit)
        resp = SearchResponse(query=query, location=display, total_results=len(raw),
                              results=[Business(**r) for r in raw])
        _cache[ck] = {"data": resp, "ts": time.time()}
        return resp
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/search-nearby", response_model=SearchResponse)
async def search_nearby(
    query: str = Query(...),
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    limit: int = Query(10, ge=1, le=20),
):
    ck = hashlib.md5(f"nearby|{query}|{lat}|{lng}|{limit}".encode()).hexdigest()
    if ck in _cache and time.time() - _cache[ck]["ts"] < CACHE_TTL:
        return _cache[ck]["data"]
    try:
        key, val = resolve_tag(query)
        raw = search_businesses(key, val, lat, lng, limit)
        resp = SearchResponse(query=query, location=f"{lat},{lng}", total_results=len(raw),
                              results=[Business(**r) for r in raw])
        _cache[ck] = {"data": resp, "ts": time.time()}
        return resp
    except Exception as e:
        raise HTTPException(500, str(e))

"""
UUID Generator API
Generate UUIDs v1, v4. Pure Python.
"""
import uuid
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

@router.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}

class UUIDResult(BaseModel):
    uuid: str
    version: int

@router.get("/")
async def root():
    return {"service": "UUID Generator API", "version": "1.1.0", "related": ["Password Strength Checker API", "Random User Generator API"]}

@router.get("/generate", response_model=UUIDResult)
async def generate(version: int = Query(4, ge=1, le=4)):
    if version == 1:
        val = str(uuid.uuid1())
    else:
        val = str(uuid.uuid4())
    return UUIDResult(uuid=val, version=version)

@router.get("/generate-batch")
async def generate_batch(
    count: int = Query(10, ge=1, le=100),
    version: int = Query(4, ge=1, le=4),
):
    vals = [str(uuid.uuid4()) if version == 4 else str(uuid.uuid1()) for _ in range(count)]
    return {"uuids": vals}

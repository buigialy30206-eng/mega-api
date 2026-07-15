"""
QR Code Generator API
Pure Python — qrcode + Pillow. Zero external APIs.
Returns PNG image.
"""

import base64
import io

import qrcode
from fastapi import APIRouter, Query
from fastapi.responses import Response, JSONResponse

router = APIRouter()

@router.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}

@router.get("/")
async def root():
    return {"service": "QR Code Generator API", "version": "1.0.0", "related": ["Barcode Generator API"]}

@router.get("/generate")
async def generate(
    text: str = Query(..., description="Text or URL to encode"),
    size: int = Query(300, ge=100, le=1000, description="Image size in pixels"),
    format: str = Query("png", description="Output format: png, base64"),
):
    """Generate QR code image."""
    qr = qrcode.QRCode(version=None, box_size=10, border=2)
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size))

    if format == "base64":
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return JSONResponse({"qr_code": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()})

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")

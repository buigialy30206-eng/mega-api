"""Mega API — 21 APIs in one Render service."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Viv Data Mega API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Import all sub-routers
from routers.whois import router as whois_router
from routers.email import router as email_router
from routers.company import router as company_router
from routers.currency import router as currency_router
from routers.qrcode import router as qrcode_router
from routers.metadata import router as metadata_router
from routers.password import router as password_router
from routers.ipgeo import router as ipgeo_router
from routers.slug import router as slug_router
from routers.ua import router as ua_router
from routers.uuid import router as uuid_router
from routers.markdown import router as markdown_router
from routers.barcode import router as barcode_router
from routers.random_user import router as random_user_router
from routers.places import router as places_router
from routers.phone import router as phone_router
from routers.vat import router as vat_router
from routers.lang import router as lang_router
from routers.sentiment import router as sentiment_router
from routers.pdf import router as pdf_router
from routers.stock import router as stock_router

# Mount sub-routers with prefixes
app.include_router(whois_router, prefix="/whois", tags=["whois"])
app.include_router(email_router, prefix="/email", tags=["email"])
app.include_router(company_router, prefix="/company", tags=["company"])
app.include_router(currency_router, prefix="/currency", tags=["currency"])
app.include_router(qrcode_router, prefix="/qrcode", tags=["qrcode"])
app.include_router(metadata_router, prefix="/metadata", tags=["metadata"])
app.include_router(password_router, prefix="/password", tags=["password"])
app.include_router(ipgeo_router, prefix="/ipgeo", tags=["ipgeo"])
app.include_router(slug_router, prefix="/slug", tags=["slug"])
app.include_router(ua_router, prefix="/ua", tags=["ua"])
app.include_router(uuid_router, prefix="/uuid", tags=["uuid"])
app.include_router(markdown_router, prefix="/markdown", tags=["markdown"])
app.include_router(barcode_router, prefix="/barcode", tags=["barcode"])
app.include_router(random_user_router, prefix="/random-user", tags=["random-user"])
app.include_router(places_router, prefix="/places", tags=["places"])
app.include_router(phone_router, prefix="/phone", tags=["phone"])
app.include_router(vat_router, prefix="/vat", tags=["vat"])
app.include_router(lang_router, prefix="/lang", tags=["lang"])
app.include_router(sentiment_router, prefix="/sentiment", tags=["sentiment"])
app.include_router(pdf_router, prefix="/pdf", tags=["pdf"])
app.include_router(stock_router, prefix="/stock", tags=["stock"])


@app.get("/health")
async def health():
    return {"status": "ok", "apis": 21}

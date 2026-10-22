from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routes.analyze import router as analyze_router
from backend.routes.upload import router as upload_router
from backend.routes.ocr import router as ocr_router
from backend.routes.forgery import router as forgery_router
from backend.routes.face import router as face_router
from backend.routes.identity import router as identity_router
from backend.routes.risk import router as risk_router
from backend.routes.report import router as report_router
from backend.services.storage_service import HEATMAPS_DIR

app = FastAPI(
    title="DocShield AI",
    description="AI-assisted identity document screening prototype. Results require human review.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:4173", "http://127.0.0.1:4173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

for router in (analyze_router, upload_router, ocr_router, forgery_router, face_router, identity_router, risk_router, report_router):
    app.include_router(router, prefix="/api")

app.mount("/heatmaps", StaticFiles(directory=str(HEATMAPS_DIR)), name="heatmaps")

@app.get("/")
def home():
    return {"project": "DocShield AI", "message": "Backend is running", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    return {"status": "healthy", "project": "DocShield AI", "version": app.version}

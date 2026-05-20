from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.database import engine
from app.auth.router import router as auth_router
from app.api.v1.router import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure media dirs exist
    for subdir in ["logos", "documents", "reports", "attachments", "gc_imports"]:
        Path(settings.MEDIA_ROOT, subdir).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="Olive Oil LIMS",
    description="Laboratory Information Management System for Olive Oil Analysis — ISO 17025 compliant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded media files
media_path = Path(settings.MEDIA_ROOT)
media_path.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(media_path)), name="media")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "olive-lims"}

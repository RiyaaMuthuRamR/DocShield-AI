from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
UPLOAD_ROOT = BACKEND_ROOT / "uploads"
ORIGINALS_DIR = UPLOAD_ROOT / "originals"
HEATMAPS_DIR = UPLOAD_ROOT / "heatmaps"
TEMP_DIR = UPLOAD_ROOT / "temp"
REPORTS_DIR = BACKEND_ROOT / "reports"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

for directory in (ORIGINALS_DIR, HEATMAPS_DIR, TEMP_DIR, REPORTS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

async def save_image_upload(file: UploadFile) -> tuple[Path, str]:
    """Validate and safely save an uploaded raster image with a unique name."""
    original_name = Path(file.filename or "document").name
    suffix = Path(original_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=415, detail="Upload a JPG, JPEG, PNG, WEBP, or BMP image.")

    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Maximum upload size is 10 MB.")

    try:
        from io import BytesIO
        with Image.open(BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid image.")

    safe_name = f"{uuid4().hex}{suffix}"
    destination = ORIGINALS_DIR / safe_name
    destination.write_bytes(content)
    return destination, original_name

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.services.ocr_service import extract_text, parse_document
from backend.services.storage_service import save_image_upload

router = APIRouter(prefix="/ocr", tags=["OCR"])

@router.post("")
async def ocr_document(file: UploadFile = File(...)):
    path, original_name = await save_image_upload(file)
    try:
        raw_text = extract_text(path)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"OCR could not run. Install dependencies from requirements.txt and retry. Details: {exc}") from exc
    return {"filename": original_name, "structured_data": parse_document(raw_text), "raw_text": raw_text}

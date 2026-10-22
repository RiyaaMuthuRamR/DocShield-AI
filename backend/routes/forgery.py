from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.services.forgery_service import analyze_document
from backend.services.storage_service import save_image_upload

router = APIRouter(prefix="/forgery", tags=["Forgery Screening"])

@router.post("")
async def detect_forgery(file: UploadFile = File(...)):
    path, original_name = await save_image_upload(file)
    try:
        result = analyze_document(path)
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    heatmap_name = Path(result["heatmap_path"]).name
    return {"filename": original_name, **{key: value for key, value in result.items() if key != "heatmap_path"}, "heatmap_url": f"/heatmaps/{heatmap_name}"}

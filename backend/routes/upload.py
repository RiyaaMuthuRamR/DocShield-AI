from fastapi import APIRouter, File, UploadFile

from backend.services.storage_service import save_image_upload

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("")
async def upload_document(file: UploadFile = File(...)):
    path, original_name = await save_image_upload(file)
    return {"message": "Document uploaded", "filename": original_name, "file_id": path.name}

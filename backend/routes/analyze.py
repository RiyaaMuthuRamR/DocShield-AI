
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image

from backend.services.forgery_service import analyze_document as analyze_forgery
from backend.services.ocr_service import extract_text, parse_document
from backend.services.risk_service import calculate_risk
from backend.services.storage_service import save_image_upload

router = APIRouter(prefix="/analyze", tags=["Combined Screening"])


@router.post("")
async def analyze_uploaded_document(file: UploadFile = File(...)):
    path, original_name = await save_image_upload(file)

    ocr_error = None
    try:
        raw_text = extract_text(path)
        ocr_data = parse_document(raw_text)
    except Exception as exc:
        raw_text = []
        ocr_data = parse_document([])
        ocr_error = str(exc)

    try:
        forgery_data = analyze_forgery(path)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Forgery analysis failed: {exc}",
        ) from exc

    try:
        with Image.open(path) as image:
            metadata_status = (
                "Present" if len(image.getexif()) else "Missing"
            )
    except Exception:
        metadata_status = "Unknown"

    heatmap_url = f"/heatmaps/{Path(forgery_data['heatmap_path']).name}"
    forgery_data = {
        key: value
        for key, value in forgery_data.items()
        if key != "heatmap_path"
    }
    forgery_data["heatmap_url"] = heatmap_url
    forgery_data["metadata_status"] = metadata_status

    risk_data = calculate_risk(
        ocr_data,
        {
            "confidence": forgery_data.get("confidence", 0),
            "metadata_status": metadata_status,
        },
    )

    qr_data = {
        "available": False,
        "valid": False,
        "data": None,
        "message": "QR analysis is unavailable.",
    }
    try:
        import cv2

        image = cv2.imread(str(path))
        if image is not None:
            qr_value, points, _ = cv2.QRCodeDetector().detectAndDecode(image)
            qr_data = {
                "available": True,
                "valid": bool(qr_value),
                "data": qr_value or None,
                "message": (
                    "QR payload decoded; verify its source separately."
                    if qr_value
                    else "No decodable QR code detected."
                ),
            }
    except Exception:
        qr_data["message"] = "QR analysis is unavailable."

    return {
        "filename": original_name,
        "file_id": path.name,
        "ocr": {
            "structured_data": ocr_data,
            "raw_text": raw_text,
            "error": ocr_error,
        },
        "forgery": forgery_data,
        "metadata_status": metadata_status,
        "qr": qr_data,
        "risk": risk_data,
        "notes": [
            "The detected document type is based on visible text patterns.",
            "ELA is a heuristic indicator, not proof of forgery.",
            "A payment screenshot does not prove that a transaction occurred.",
            "Identity consistency comparison is not part of this version.",
        ],
    }

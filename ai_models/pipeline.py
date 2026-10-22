from ai_models.ocr.ocr_engine import extract_text
from ai_models.qr.qr_validator import validate_qr
from ai_models.forgery.metadata_analyzer import analyze_metadata
from ai_models.forgery.forgery_detector import detect_forgery


def analyze_document(image_path):
    """
    Run all CSE-2 document analysis modules.
    """

    # OCR + MRZ
    ocr_result = extract_text(image_path)

    # QR validation
    qr_result = validate_qr(image_path)

    # Image metadata
    metadata_result = analyze_metadata(image_path)

    # Forgery detection
    forgery_result = detect_forgery(image_path)

    return {
        "ocr": ocr_result,
        "qr": qr_result,
        "metadata": metadata_result,
        "forgery": forgery_result
    }
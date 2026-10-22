from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from backend.app import app

client = TestClient(app)

def make_png() -> bytes:
    image = Image.new("RGB", (320, 180), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_identity_match_does_not_require_same_number_for_different_types():
    response = client.post("/api/identity-check", json={
        "document1": {"name": "Alex Example", "dob": "01/02/2000", "document_number": "P1234567", "document_type": "passport"},
        "document2": {"name": "Alex Example", "dob": "01/02/2000", "document_number": "ABCDE1234F", "document_type": "pan"},
    })
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "MATCHED"
    assert body["checks"]["document_number_comparable"] is False

def test_analyze_endpoint_returns_screening_result_even_without_optional_ocr_model():
    response = client.post("/api/analyze", files={"file": ("sample.png", make_png(), "image/png")})
    assert response.status_code == 200
    body = response.json()
    assert "ocr" in body and "forgery" in body and "risk" in body
    assert 0 <= body["risk"]["overall_risk"] <= 100
    assert body["identity_status"] == "NOT_CHECKED"

def test_report_generate_and_download():
    payload = {
        "ocr": {"name": "Sample Person", "dob": "01/01/2000", "document_number": "P1234567"},
        "forgery": {"confidence": 4.2, "metadata_status": "Missing"},
        "risk": {"overall_risk": 15, "status": "LOW RISK — REVIEW STILL REQUIRED", "reasons": ["Sample reason"]},
    }
    response = client.post("/api/report", json=payload)
    assert response.status_code == 200
    report_id = response.json()["report_id"]
    downloaded = client.get(response.json()["download_url"])
    assert downloaded.status_code == 200
    assert downloaded.headers["content-type"] == "application/pdf"
    assert downloaded.content.startswith(b"%PDF")

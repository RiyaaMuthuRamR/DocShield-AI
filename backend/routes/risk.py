from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.risk_service import calculate_risk

router = APIRouter(prefix="/risk-score", tags=["Risk Engine"])

class OCRData(BaseModel):
    name: str = ""
    dob: str = ""
    document_number: str = ""

class ForgeryData(BaseModel):
    confidence: float = Field(default=0, ge=0, le=100)
    metadata_status: str = "Unknown"

class IdentityData(BaseModel):
    status: str = "NOT_CHECKED"

class RiskRequest(BaseModel):
    ocr: OCRData
    forgery: ForgeryData
    identity: IdentityData = IdentityData()

@router.post("")
def generate_risk(request: RiskRequest):
    return calculate_risk(request.ocr.model_dump(), request.forgery.model_dump(), request.identity.model_dump())

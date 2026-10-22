from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.identity_service import compare_identity

router = APIRouter(prefix="/identity-check", tags=["Identity Consistency"])

class IdentityDoc(BaseModel):
    name: str = Field(default="", max_length=120)
    dob: str = Field(default="", max_length=30)
    document_number: str = Field(default="", max_length=40)
    document_type: str = Field(default="", max_length=40)

class IdentityRequest(BaseModel):
    document1: IdentityDoc
    document2: IdentityDoc

@router.post("")
def verify_identity(request: IdentityRequest):
    return compare_identity(request.document1.model_dump(), request.document2.model_dump())

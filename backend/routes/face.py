from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/face-verify", tags=["Face Verification"])

@router.post("")
def face_verification_status():
    raise HTTPException(
        status_code=501,
        detail="Face verification is not implemented in this project copy. Do not treat this endpoint as a real face match."
    )


import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.services.report_service import create_report
from backend.services.storage_service import REPORTS_DIR

router = APIRouter(prefix="/report", tags=["Investigation Reports"])


class ReportRequest(BaseModel):
    ocr: dict[str, Any] = Field(default_factory=dict)
    forgery: dict[str, Any] = Field(default_factory=dict)
    risk: dict[str, Any] = Field(default_factory=dict)
    metadata_status: str = "Unknown"


@router.post("")
def generate_report(request: ReportRequest):
    report_data = request.model_dump()
    report_data["metadata_status"] = (
        report_data.get("metadata_status")
        or report_data.get("forgery", {}).get("metadata_status")
        or "Unknown"
    )
    report_id, _path = create_report(report_data)

    return {
        "report_id": report_id,
        "download_url": f"/api/report/download/{report_id}",
        "message": "Investigation report generated",
    }


@router.get("/download/{report_id}")
def download_report(report_id: str):
    if not re.fullmatch(r"INV-[A-Z0-9-]+", report_id):
        raise HTTPException(status_code=400, detail="Invalid report ID")

    path: Path = REPORTS_DIR / f"{report_id}.pdf"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"{report_id}.pdf",
    )

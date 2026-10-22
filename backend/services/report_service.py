
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from uuid import uuid4

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .storage_service import REPORTS_DIR


def create_report(data: dict) -> tuple[str, Path]:
    report_id = (
        f"INV-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-"
        f"{uuid4().hex[:6].upper()}"
    )
    pdf_path = REPORTS_DIR / f"{report_id}.pdf"
    styles = getSampleStyleSheet()

    ocr = data.get("ocr", {})
    document_type = ocr.get("document_type", "general_document")
    labels = {
        "payment_receipt": "Payment receipt",
        "identity_document": "Identity document",
        "general_document": "General document",
    }
    fields = ocr.get("extracted_fields", {})

    if not fields:
        if document_type == "payment_receipt":
            fields = {
                "Amount": ocr.get("amount"),
                "Recipient": ocr.get("recipient"),
                "Transaction date/time": ocr.get("transaction_date"),
                "Transaction ID": ocr.get("transaction_id"),
            }
        else:
            fields = {
                "Name": ocr.get("name"),
                "Date of birth": ocr.get("dob"),
                "Document number": ocr.get("document_number"),
            }

    table_data = [["Field", "Extracted value"]]
    for label, value in fields.items():
        table_data.append([
            escape(str(label)),
            escape(str(value or "Not extracted")),
        ])

    story = [
        Paragraph("DocShield AI — Investigation Screening Report", styles["Title"]),
        Spacer(1, 10),
        Paragraph(f"Investigation ID: {escape(report_id)}", styles["Normal"]),
        Paragraph(
            "Generated (UTC): "
            + escape(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")),
            styles["Normal"],
        ),
        Spacer(1, 12),
        Paragraph(
            "Detected document type: "
            + escape(labels.get(document_type, document_type)),
            styles["Heading2"],
        ),
        Spacer(1, 6),
        Paragraph("Extracted fields", styles["Heading2"]),
    ]

    table = Table(table_data, colWidths=[150, 320], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173B35")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5D1")),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    story += [table, Spacer(1, 14)]
    forgery = data.get("forgery", {})
    story.append(Paragraph("Tampering screening", styles["Heading2"]))
    story.append(Paragraph(
        "ELA indicator: "
        + escape(str(forgery.get("confidence", "Not available")))
        + " (heuristic, not a probability)",
        styles["Normal"],
    ))
    story.append(Paragraph(
        "Metadata status: "
        + escape(str(data.get("metadata_status", "Unknown"))),
        styles["Normal"],
    ))

    risk = data.get("risk", {})
    story += [
        Spacer(1, 12),
        Paragraph("Risk screening", styles["Heading2"]),
        Paragraph(
            "Screening score: "
            + escape(str(risk.get("overall_risk", "Not available")))
            + " / 100",
            styles["Normal"],
        ),
        Paragraph(
            "Status: " + escape(str(risk.get("status", "Not available"))),
            styles["Normal"],
        ),
        Spacer(1, 8),
        Paragraph("Reasons", styles["Heading3"]),
    ]

    for reason in risk.get("reasons", []):
        story.append(Paragraph("• " + escape(str(reason)), styles["Normal"]))
        story.append(Spacer(1, 3))

    story += [
        Spacer(1, 14),
        Paragraph("Important limitation", styles["Heading2"]),
        Paragraph(
            "This prototype provides screening indicators only. OCR can be incorrect, "
            "ELA can produce false positives, and missing metadata does not prove fraud. "
            "A payment screenshot alone cannot confirm that money was transferred. "
            "Verify payment claims with the relevant payment provider and have identity "
            "documents checked through an authorized trusted source.",
            styles["Normal"],
        ),
    ]

    SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        title="DocShield AI Investigation Report",
    ).build(story)

    return report_id, pdf_path

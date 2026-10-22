
def calculate_risk(
    ocr_data: dict,
    forgery_data: dict,
    identity_data: dict | None = None,
) -> dict:
    """Calculate a document-type-aware screening score, not a fraud probability."""
    score = 0
    reasons = []
    document_type = ocr_data.get("document_type", "general_document")

    if document_type == "payment_receipt":
        if not ocr_data.get("amount"):
            score += 10
            reasons.append("Payment amount was not extracted.")
        if not ocr_data.get("recipient"):
            score += 10
            reasons.append("Payment recipient was not extracted.")
        if not ocr_data.get("transaction_date"):
            score += 5
            reasons.append("Transaction date/time was not extracted.")
        if not ocr_data.get("transaction_id"):
            reasons.append(
                "Transaction ID was not extracted; some genuine receipts may not show one."
            )

    elif document_type == "identity_document":
        if not ocr_data.get("name"):
            score += 10
            reasons.append("Name was not extracted.")
        if not ocr_data.get("document_number"):
            score += 15
            reasons.append("Document number was not extracted.")
        # DOB is optional for some identity documents.
        if not ocr_data.get("dob"):
            reasons.append("Date of birth was not extracted; it may not appear on every document.")

    else:
        reasons.append(
            "Document type could not be identified confidently. Review the extracted text manually."
        )
        score += 10

    try:
        indicator = float(forgery_data.get("confidence", 0) or 0)
    except (TypeError, ValueError):
        indicator = 0

    # Existing ELA confidence is a heuristic indicator, not a probability.
    if indicator >= 15:
        score += 25
        reasons.append("Elevated ELA indicator; inspect the heatmap manually.")
    elif indicator >= 5:
        score += 10
        reasons.append("ELA indicator detected; manual inspection is recommended.")

    if forgery_data.get("metadata_status") == "Missing":
        score += 5
        reasons.append(
            "Image metadata is absent; this alone is not evidence of forgery."
        )

    score = min(score, 100)

    if score < 20:
        status, color = "LOW SCREENING FLAGS — REVIEW STILL REQUIRED", "GREEN"
    elif score < 50:
        status, color = "NEEDS REVIEW", "YELLOW"
    else:
        status, color = "ELEVATED SCREENING FLAGS", "RED"

    if not reasons:
        reasons.append(
            "No configured screening flags were triggered; this does not prove authenticity."
        )

    return {
        "overall_risk": score,
        "status": status,
        "color": color,
        "document_type": document_type,
        "reasons": reasons,
        "disclaimer": (
            "Heuristic screening score, not a probability of fraud. "
            "OCR and ELA can be wrong. Verify payment claims with the payment provider "
            "and identity documents with an authorized trusted source."
        ),
    }

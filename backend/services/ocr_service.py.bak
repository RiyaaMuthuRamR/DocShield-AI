
import os
import re
import shutil
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _get_reader():
    """Load EasyOCR only when OCR is needed."""
    try:
        import easyocr
        return easyocr.Reader(["en"], gpu=False)
    except ImportError:
        return None


def _extract_with_tesseract(image_path: str | Path) -> list[str]:
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "OCR requires EasyOCR or pytesseract. Install requirements.txt."
        ) from exc

    configured_path = os.getenv("TESSERACT_CMD")
    if configured_path:
        pytesseract.pytesseract.tesseract_cmd = configured_path
    elif not shutil.which("tesseract"):
        windows_path = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        if windows_path.is_file():
            pytesseract.pytesseract.tesseract_cmd = str(windows_path)

    try:
        with Image.open(image_path) as image:
            text = pytesseract.image_to_string(image)
    except Exception as exc:
        raise RuntimeError(
            "OCR could not run. Install Tesseract OCR and add it to PATH, "
            "or install EasyOCR. Details: " + str(exc)
        ) from exc

    return [line.strip() for line in text.splitlines() if line.strip()]


def extract_text(image_path: str | Path) -> list[str]:
    reader = _get_reader()
    if reader is None:
        return _extract_with_tesseract(image_path)

    results = reader.readtext(str(image_path), detail=1, paragraph=False)
    return [
        str(item[1]).strip()
        for item in results
        if len(item) > 1 and str(item[1]).strip()
    ]


def detect_document_type(text_list: list[str]) -> str:
    """Classify using visible text patterns; this is a heuristic."""
    text = " ".join(text_list).lower()

    receipt_terms = (
        "paid to", "payment successful", "transaction id",
        "upi", "upi ref", "banking name", "paid successfully",
        "payment details", "credited to", "debited from",
        "transaction successful", "paid on", "transfer successful",
    )
    identity_terms = (
        "date of birth", "dob", "passport", "identity card",
        "national identity", "driving licence", "driving license",
        "aadhaar", "permanent account number", "pan card",
        "identity document", "date of issue", "place of birth",
    )

    receipt_score = sum(term in text for term in receipt_terms)
    identity_score = sum(term in text for term in identity_terms)

    if receipt_score > identity_score and receipt_score > 0:
        return "payment_receipt"
    if identity_score > 0:
        return "identity_document"
    return "general_document"


def parse_document(text_list: list[str]) -> dict:
    """Extract fields appropriate to the detected document category."""
    full_text = "\n".join(text_list)
    upper_text = full_text.upper()
    document_type = detect_document_type(text_list)

    data = {
        "document_type": document_type,
        "name": "",
        "dob": "",
        "document_number": "",
        "amount": "",
        "recipient": "",
        "transaction_date": "",
        "transaction_id": "",
        "extracted_fields": {},
    }

    if document_type == "payment_receipt":
        # Common Indian payment receipt formats, including UPI screenshots.
        amount_match = re.search(
            r"(?:₹|RS\.?\s*)([\d,]+(?:\.\d{1,2})?)",
            upper_text,
        )
        if amount_match:
            data["amount"] = "₹" + amount_match.group(1)

        recipient_patterns = [
            r"PAID\s+TO\s*[:\-]?\s*([A-Z][A-Z .'-]{2,70})",
            r"(?:RECIPIENT|PAYEE|SENT\s+TO)\s*[:\-]\s*([A-Z][A-Z .'-]{2,70})",
            r"BANKING\s+NAME\s*:\s*([A-Z][A-Z .'-]{2,70})",
        ]
        for pattern in recipient_patterns:
            match = re.search(pattern, upper_text)
            if match:
                recipient = match.group(1).strip(" .:-")
                recipient = re.split(
                    r"\s{2,}|TRANSACTION|UPI|BANKING NAME|20\d{2}",
                    recipient,
                )[0].strip()
                if len(recipient) >= 3:
                    data["recipient"] = recipient.title()
                    break

        date_match = re.search(
            r"\b(?:\d{1,2}\s+[A-Z]{3,9}\s+20\d{2}"
            r"|\d{1,2}[/-]\d{1,2}[/-]20\d{2}"
            r"|20\d{2}[/-]\d{1,2}[/-]\d{1,2})"
            r"(?:[, ]+\d{1,2}:\d{2}\s*(?:AM|PM)?)?",
            upper_text,
        )
        if date_match:
            data["transaction_date"] = date_match.group(0).strip()

        transaction_patterns = [
            r"(?:UPI\s*(?:REF(?:ERENCE)?|ID)|TRANSACTION\s*ID|"
            r"TXN\s*ID|UTR)\s*[:#\-]?\s*([A-Z0-9-]{6,40})",
        ]
        for pattern in transaction_patterns:
            match = re.search(pattern, upper_text)
            if match:
                data["transaction_id"] = match.group(1).strip()
                break

        data["extracted_fields"] = {
            "Amount": data["amount"] or "Not extracted",
            "Recipient": data["recipient"] or "Not extracted",
            "Transaction date/time": data["transaction_date"] or "Not extracted",
            "Transaction ID": data["transaction_id"] or "Not extracted",
        }
        return data

    # Identity/general document extraction.
    dob_match = re.search(
        r"\b(?:\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})\b",
        full_text,
    )
    if dob_match:
        data["dob"] = dob_match.group(0)

    number_patterns = [
        r"\b[A-Z][0-9]{7}\b",
        r"\b[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}\b",
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    ]
    for pattern in number_patterns:
        match = re.search(pattern, upper_text)
        if match:
            data["document_number"] = re.sub(r"\s+", "", match.group(0))
            break

    ignore_terms = (
        "INSTITUTE", "COLLEGE", "UNIVERSITY", "TECHNOLOGY",
        "ENGINEERING", "INDIA", "GOVERNMENT", "PROFESSOR",
        "ASSISTANT", "STUDENT", "FACULTY", "CARD", "IDENTITY",
        "DEPARTMENT", "DATE OF BIRTH", "PASSPORT", "REPUBLIC",
        "DATE OF ISSUE", "VALID UNTIL", "DOB",
    )

    for line in text_list:
        candidate = line.strip()
        normalized = candidate.upper()
        if any(word in normalized for word in ignore_terms):
            continue
        if re.search(r"\d", candidate):
            continue
        if len(candidate.split()) < 2 or len(candidate) > 60:
            continue
        if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]+", candidate):
            continue
        data["name"] = candidate.title()
        break

    data["extracted_fields"] = {
        "Name": data["name"] or "Not extracted",
        "Date of birth": data["dob"] or "Not extracted",
        "Document number": data["document_number"] or "Not extracted",
    }
    return data

from pathlib import Path
import re

path = Path("backend/services/ocr_service.py")
source = path.read_text(encoding="utf-8")

start = '    if document_type == "payment_receipt":'
end = "    dob_match = re.search("

start_index = source.find(start)
end_index = source.find(end, start_index + len(start))

if start_index < 0 or end_index < 0:
    raise SystemExit(
        "Patch stopped safely: expected code markers were not found. "
        "No changes made."
    )

backup = path.with_name("ocr_service.py.bak")
if not backup.exists():
    backup.write_text(source, encoding="utf-8")

replacement = r'''    if document_type == "payment_receipt":
        # First, prefer amounts explicitly marked with a currency symbol.
        amount_match = re.search(
            r"(?:₹|RS\.?\s*)([\d,]+(?:\.\d{1,2})?)",
            upper_text,
        )

        if amount_match:
            data["amount"] = "₹" + amount_match.group(1)
        else:
            # OCR may read the rupee symbol as '*'.
            # Only use this fallback when a line contains just an amount.
            for line in text_list:
                candidate = line.strip()
                fallback = re.fullmatch(
                    r"[*₹$]\s*([\d,]+(?:\.\d{1,2})?)",
                    candidate,
                )
                if fallback:
                    data["amount"] = "₹" + fallback.group(1)
                    break

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

        # Accept dates with month names or numeric date formats,
        # and times using either ':' or '.' (e.g. 7:44 PM or 7.44 PM).
        date_match = re.search(
            r"\b(?:"
            r"\d{1,2}\s+[A-Z]{3,9}\s+20\d{2}"
            r"|\d{1,2}[/-]\d{1,2}[/-]20\d{2}"
            r"|20\d{2}[/-]\d{1,2}[/-]\d{1,2}"
            r")"
            r"(?:\s*,?\s*\d{1,2}[.:]\d{2}\s*(?:AM|PM)?)?",
            upper_text,
        )
        if date_match:
            data["transaction_date"] = date_match.group(0).strip(" ,")

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

'''

updated = source[:start_index] + replacement + source[end_index:]
path.write_text(updated, encoding="utf-8")
print("Receipt parser updated.")
print(f"Backup saved at: {backup}")

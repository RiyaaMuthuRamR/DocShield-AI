import os
import re
import pytesseract

# Use the system PATH by default. Set TESSERACT_CMD if Tesseract is installed
# at a non-standard location; avoid hard-coding a single developer's Windows path.
_tesseract_cmd = os.getenv("TESSERACT_CMD")
if _tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd

from .preprocessing import preprocess_image, preprocess_mrz
from .mrz_parser import parse_mrz


def normalize_mrz_line(line):
    line = line.upper().strip()

    # Keep only valid MRZ characters
    line = re.sub(r"[^A-Z0-9<]", "", line)

    # Common OCR confusion
    line = line.replace("1ND", "IND")

    return line


def prepare_lines(mrz_text):
    lines = [
        normalize_mrz_line(line)
        for line in mrz_text.splitlines()
        if line.strip()
    ]

    candidates = [
        line
        for line in lines
        if line.startswith("P<") or len(line) >= 30
    ]

    if len(candidates) < 2:
        return None

    fixed = []

    for line in candidates[:2]:

        if len(line) < 44:
            line = line.ljust(44, "<")

        fixed.append(line[:44])

    return fixed


def generate_candidates(lines):
    """
    Generate possible MRZ candidates.

    OCR can confuse '<' with letters or miss
    the final composite check digit.

    We generate candidates, but never blindly
    declare an OCR-recovered document as valid.
    """

    line1, line2 = lines

    candidates = []

    # Original OCR result
    candidates.append(
        (line1, line2, False)
    )

    # ---------------------------------------------
    # Optional-data correction
    # ---------------------------------------------

    optional_data = line2[28:43]

    for index, char in enumerate(optional_data):

        if char != "<":

            modified = list(line2)

            modified[28 + index] = "<"

            candidates.append(
                (
                    line1,
                    "".join(modified),
                    False
                )
            )

    # ---------------------------------------------
    # Composite check-digit recovery
    # ---------------------------------------------

    # Position 43 = final composite check digit
    for digit in "0123456789":

        modified = list(line2)

        modified[43] = digit

        candidates.append(
            (
                line1,
                "".join(modified),
                True
            )
        )

    return candidates


def build_ocr_result(text, mrz_result):
    """
    Create a clean OCR response for the rest
    of the DocShield system.
    """

    return {
        "document_text": text,
        "mrz": mrz_result,
        "mrz_status": mrz_result.get(
            "validation_status",
            "UNKNOWN"
        ),
        "mrz_valid": mrz_result.get(
            "valid",
            False
        )
    }


def extract_text(image_path):

    # =============================================
    # FULL DOCUMENT OCR
    # =============================================

    image = preprocess_image(image_path)

    text = pytesseract.image_to_string(image)

    # =============================================
    # MRZ OCR
    # =============================================

    mrz_image = preprocess_mrz(image_path)

    psm_modes = [6, 11]

    mrz_candidates = []

    # Run multiple OCR modes
    for psm in psm_modes:

        mrz_text = pytesseract.image_to_string(
            mrz_image,
            config=(
                f"--psm {psm} "
                "-c tessedit_char_whitelist="
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
            )
        )

        lines = prepare_lines(mrz_text)

        if lines:

            candidates = generate_candidates(lines)

            mrz_candidates.extend(candidates)

    # =============================================
    # REMOVE DUPLICATE CANDIDATES
    # =============================================

    unique_candidates = []

    seen = set()

    for line1, line2, recovered in mrz_candidates:

        key = (line1, line2)

        if key not in seen:

            seen.add(key)

            unique_candidates.append(
                (line1, line2, recovered)
            )

    # =============================================
    # STRICT MRZ VALIDATION
    # =============================================

    for line1, line2, recovered in unique_candidates:

        result = parse_mrz(
            line1 + "\n" + line2
        )

        if result.get("valid"):

            # If composite check digit was recovered
            # instead of directly trusted from OCR,
            # keep the document OCR_UNCERTAIN.
            if recovered:

                result["valid"] = False

                result["validation_status"] = (
                    "OCR_UNCERTAIN"
                )

                result["message"] = (
                    "MRZ fields validated, "
                    "but composite check digit "
                    "was recovered from OCR uncertainty"
                )

                result["recovered_composite_check_digit"] = (
                    line2[43]
                )

            return build_ocr_result(
                text,
                result
            )

    # =============================================
    # NO FULLY VALID CANDIDATE
    # =============================================

    if unique_candidates:

        line1, line2, recovered = unique_candidates[0]

        result = parse_mrz(
            line1 + "\n" + line2
        )

        return build_ocr_result(
            text,
            result
        )

    # =============================================
    # MRZ NOT FOUND
    # =============================================

    return build_ocr_result(
        text,
        {
            "valid": False,
            "validation_status": "INVALID",
            "message": "MRZ could not be extracted",
            "lines": []
        }
    )